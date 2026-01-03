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
from send_nurture_email import send_follow_up_email, send_no_interest_email
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
            details = gmail.get_latest_message_details(latest_thread['id'], skip_my_email=not is_test)
            
            if details and details.get('body'):
                print(f"REPLY DETECTED from {biz_name}. Analyzing sentiment...")
                sentiment = analyzer.classify_response(details['body'])
                print(f"SENTIMENT: {sentiment}")
                
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
                    
                    result = send_no_interest_email(recipient, lead_name, thread_info=thread_info)
                    if result['success']:
                        sheets.update_cell(f"J{i}", "Archived (Not Interested)", tab_name)
                        print(f"SUCCESS: Archived {biz_name} and replied in thread.")
                    continue
                
                elif sentiment == "Interested":
                    print(f"LEAD INTERESTED: {biz_name}! Drafting context-aware reply...")
                    recipient = my_email if is_test else email
                    
                    # Use the AI to draft a personalized reply based on the lead's email
                    drafted_body = drafter.draft_reply(details['body'], lead_name)
                    
                    # Prepare thread info for reply
                    thread_info = {
                        'gmail_client': gmail,
                        'thread_id': details['thread_id'],
                        'message_id': details['message_id'],
                        'subject': details['subject']
                    }
                    
                    result = send_interested_reply(recipient, lead_name, thread_info=thread_info, custom_body=drafted_body)
                    if result['success']:
                        sheets.update_cell(f"J{i}", "Interested (Booking Link Sent)", tab_name)
                        print(f"SUCCESS: Sent drafted reply to {biz_name} and updated sheet.")
                    continue
                
                elif sentiment == "Neutral":
                    print(f"LEAD NEUTRAL: {biz_name}. Manual review suggested.")
                    sheets.update_cell(f"J{i}", "Pending (Neutral Reply)", tab_name)

        # 2. Logic: Follow-up after 1 week if no response
        if contacted == "yes" and status in ["", "pending", "none"] and followup_count < 1:
            try:
                try:
                    last_contact = datetime.strptime(last_contact_str.split(' ')[0], "%Y-%m-%d")
                except:
                    continue
                
                if (today - last_contact).days >= 7:
                    print(f"FOLLOW-UP REQUIRED: {biz_name} ({email})")
                    recipient = my_email if is_test else email
                    result = send_follow_up_email(recipient, lead_name, biz_name)
                    if result['success']:
                        sheets.update_cell(f"J{i}", "Followed Up", tab_name)
                        sheets.update_cell(f"K{i}", str(followup_count + 1), tab_name)
                        sheets.update_cell(f"I{i}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tab_name)
                        print(f"SUCCESS: Sent follow-up to {biz_name}")
            except Exception as e:
                print(f"FAILED: Follow-up for {biz_name}: {e}")

    print(f"--- MAINTENANCE COMPLETE ---")

if __name__ == "__main__":
    import sys
    tab = sys.argv[1] if len(sys.argv) > 1 else "Sheet1"
    is_test_mode = "test" in sys.argv
    asyncio.run(maintain_leads(tab, is_test=is_test_mode))
