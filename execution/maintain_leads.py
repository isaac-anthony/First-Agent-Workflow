#!/usr/bin/env python3
"""
Layer 2: Orchestration Script (Janitor Mode)
Lead Maintenance & Nurture Agent
Monitors Google Sheets and automates follow-ups.
Now with Threaded Gmail replies and advanced sentiment analysis.
"""

import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google_sheets_client import GoogleSheetsClient
from gmail_client import GmailClient
from sentiment_analyzer import SentimentAnalyzer
from drafting_agent import DraftingAgent
from learning_agent import LearningAgent
from notifier_agent import NotifierAgent
from send_nurture_email import (
    send_follow_up_stage_1, 
    send_follow_up_stage_2, 
    send_follow_up_stage_3, 
    send_no_interest_email,
    send_welcome_back_email
)
from send_interested_email import send_interested_reply

load_dotenv()

async def maintain_leads(tab_name: str = "Sheet1", is_test: bool = False):
    """
    Watches the Google Sheet and handles follow-ups, replies, or status changes.
    """
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
    if not spreadsheet_id:
        print("ERROR: GOOGLE_SHEETS_ID missing in .env")
        return

    sheets = GoogleSheetsClient(spreadsheet_id)
    gmail = GmailClient()
    analyzer = SentimentAnalyzer()
    drafter = DraftingAgent()
    learner = LearningAgent()
    notifier = NotifierAgent()
    
    rows = sheets.get_all_values(tab_name)
    
    if not rows or len(rows) <= 1:
        print(f"No leads found in tab: {tab_name}")
        return

    headers = rows[0]
    lead_rows = rows[1:]
    
    try:
        col_name = headers.index("Business Name")
        col_lead_name = headers.index("Lead Name")
        col_email = headers.index("Email")
        col_date_added = headers.index("Date Added")
        col_contacted = headers.index("Contacted?")
        col_time_contacted = headers.index("Time Contacted")
        col_status = headers.index("Status")
        col_followup_count = headers.index("Follow-up Count")
    except ValueError as e:
        print(f"ERROR: Missing required columns in sheet: {e}")
        return

    print(f"--- STARTING LEAD MAINTENANCE ('{tab_name}') ---")
    today = datetime.now()
    my_email = os.getenv('EMAIL_FROM', '04isaacag@gmail.com')
    
    for i, row in enumerate(lead_rows, start=2):
        while len(row) < len(headers):
            row.append("")
            
        biz_name = row[col_name]
        lead_name = row[col_lead_name]
        email = row[col_email]
        status = row[col_status].strip().lower()
        contacted = row[col_contacted].strip().lower()
        followup_count = int(row[col_followup_count]) if row[col_followup_count] and str(row[col_followup_count]).isdigit() else 0
        last_contact_str = row[col_time_contacted] or row[col_date_added]

        if status in ["archived (not interested)", "interested"]:
            continue

        # 1. Logic: Check for Gmail replies
        if is_test:
            # For test mode, the business name might be long or have special chars.
            # We search for the first 3 words of the business name to be safe.
            short_biz = " ".join(biz_name.split()[:3]).replace("|", "").strip()
            search_query = f'"{short_biz}"'
            print(f"TEST MODE: Searching for thread with keyword '{short_biz}'...")
        else:
            search_query = f"from:{email}"
            print(f"Checking for replies from: {email}...")

        threads = gmail.search_threads(search_query)
        
        if threads:
            latest_thread = threads[0]
            
            # Run Learning Agent on the thread
            print(f"🧠 RECURSIVE BRAIN: Analyzing thread patterns for {biz_name}...")
            thread_msgs = gmail.get_full_thread_messages(latest_thread['id'])
            learner.analyze_thread(thread_msgs)

            details = gmail.get_latest_message_details(latest_thread['id'], skip_my_email=not is_test)
            
            if details and details.get('body'):
                print(f"REPLY DETECTED from {biz_name}. Analyzing sentiment...")
                sentiment = analyzer.classify_response(details['body'])
                print(f"SENTIMENT: {sentiment}")
                
                # Use extracted sender name if available for better personalization
                actual_name = details.get('sender_name', lead_name)
                if actual_name and actual_name != lead_name and actual_name != "Team":
                    print(f"Updating Lead Name in sheet: {lead_name} -> {actual_name}")
                    sheets.update_cell(f"B{i}", actual_name, tab_name) # Column B is Lead Name
                
                if sentiment == "Not Interested":
                    print(f"LEAD REJECTED: {biz_name}. Sending demo video as REPLY...")
                    recipient = my_email if is_test else email
                    
                    # Prepare thread info for reply
                    thread_info = {
                        'gmail_client': gmail,
                        'thread_id': details['thread_id'],
                        'message_id': details['message_id'],
                        'subject': details['subject']
                    }
                    
                    result = send_no_interest_email(recipient, actual_name, thread_info=thread_info)
                    if result['success']:
                        sheets.update_cell(f"J{i}", "Archived (Not Interested)", tab_name)
                        print(f"SUCCESS: Archived {biz_name} and replied in thread.")
                    continue
                
                elif sentiment == "Interested":
                    print(f"LEAD INTERESTED: {biz_name}! Drafting context-aware reply...")
                    recipient = my_email if is_test else email
                    
                    # Notify Slack
                    print(f"✅ INTEREST DETECTED: {biz_name}! Sending Slack Alert...")
                    notifier.notify_interest(biz_name, actual_name, email, sentiment, details['body'][:200])

                    # Use the AI to draft a personalized reply based on the lead's email
                    drafted_body = drafter.draft_reply(details['body'], actual_name)
                    
                    # Prepare thread info for reply
                    thread_info = {
                        'gmail_client': gmail,
                        'thread_id': details['thread_id'],
                        'message_id': details['message_id'],
                        'subject': details['subject']
                    }
                    
                    result = send_interested_reply(recipient, actual_name, thread_info=thread_info, custom_body=drafted_body)
                    if result['success']:
                        sheets.update_cell(f"J{i}", "Interested (Booking Link Sent)", tab_name)
                        print(f"SUCCESS: Sent drafted reply to {biz_name} and updated sheet.")
                    continue
                
                elif sentiment == "OOO":
                    print(f"LEAD OOO: {biz_name}. Rescheduling follow-up by 7 days.")
                    reschedule_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
                    sheets.update_cell(f"I{i}", reschedule_date, tab_name) # Push back 'Time Contacted'
                    sheets.update_cell(f"J{i}", "OOO (Rescheduled)", tab_name)
                    continue

                elif sentiment == "Neutral":
                    print(f"LEAD NEUTRAL: {biz_name}. Manual review suggested.")
                    sheets.update_cell(f"J{i}", "Pending (Neutral Reply)", tab_name)

        # 2. Logic: Multi-Stage Follow-up if no response
        if contacted == "yes" and status in ["", "pending", "none", "followed up", "ooo (rescheduled)"]:
            try:
                try:
                    last_contact = datetime.strptime(last_contact_str.split(' ')[0], "%Y-%m-%d")
                except:
                    continue
                
                days_since_contact = (today - last_contact).days
                recipient = my_email if is_test else email
                
                # Fetch thread info for threaded follow-ups
                search_query = f'"{biz_name}"' if is_test else f"from:{email}"
                threads = gmail.search_threads(search_query)
                thread_info = None
                if threads:
                    t_details = gmail.get_latest_message_details(threads[0]['id'], skip_my_email=False)
                    if t_details:
                        thread_info = {
                            'gmail_client': gmail,
                            'thread_id': t_details['thread_id'],
                            'message_id': t_details['message_id'],
                            'subject': t_details['subject']
                        }

                # Stage 0: Welcome Back (from OOO)
                if status == "ooo (rescheduled)" and days_since_contact >= 0:
                    print(f"WELCOME BACK FOLLOW-UP (Post-OOO): {biz_name}")
                    result = send_welcome_back_email(recipient, lead_name, biz_name, thread_info=thread_info)
                    if result['success']:
                        sheets.update_cell(f"J{i}", "Followed Up (Post-OOO)", tab_name)
                        sheets.update_cell(f"I{i}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tab_name)
                    continue

                # Stage 1: Day 3 Nudge
                # FOR TEST MODE: Override days_since_contact to 0 to trigger follow-up immediately
                if followup_count == 0 and (days_since_contact >= 3 or is_test) and status != "ooo (rescheduled)":
                    print(f"FOLLOW-UP STAGE 1 (Day 3): {biz_name}")
                    result = send_follow_up_stage_1(recipient, lead_name, biz_name, thread_info=thread_info)
                    if result['success']:
                        sheets.update_cell(f"J{i}", "Followed Up (Stage 1)", tab_name)
                        sheets.update_cell(f"K{i}", "1", tab_name)
                        sheets.update_cell(f"I{i}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tab_name)
                
                # Stage 2: Day 7 Value Add
                elif followup_count == 1 and (days_since_contact >= 7 or is_test):
                    print(f"FOLLOW-UP STAGE 2 (Day 7): {biz_name}")
                    result = send_follow_up_stage_2(recipient, lead_name, biz_name, thread_info=thread_info)
                    if result['success']:
                        sheets.update_cell(f"J{i}", "Followed Up (Stage 2)", tab_name)
                        sheets.update_cell(f"K{i}", "2", tab_name)
                        sheets.update_cell(f"I{i}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tab_name)

                # Stage 3: Day 14 Break-up
                elif followup_count == 2 and days_since_contact >= 14:
                    print(f"FOLLOW-UP STAGE 3 (Day 14): {biz_name}")
                    result = send_follow_up_stage_3(recipient, lead_name, biz_name, thread_info=thread_info)
                    if result['success']:
                        sheets.update_cell(f"J{i}", "Archived (No Response)", tab_name)
                        sheets.update_cell(f"K{i}", "3", tab_name)
                        sheets.update_cell(f"I{i}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tab_name)

            except Exception as e:
                print(f"FAILED: Follow-up sequence for {biz_name}: {e}")

    print(f"--- MAINTENANCE COMPLETE ---")

if __name__ == "__main__":
    import sys
    tab = sys.argv[1] if len(sys.argv) > 1 else "Sheet1"
    is_test_mode = "test" in sys.argv
    asyncio.run(maintain_leads(tab, is_test=is_test_mode))
