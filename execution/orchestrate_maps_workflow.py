#!/usr/bin/env python3
"""
Layer 2: Orchestration Script
Google Maps Small Business Workflow
Integrates scraping, extraction, Google Sheets, and Automated Outreach.
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from scrape_google_maps import scrape_google_maps
from extract_website_data import extract_emails_from_url
from google_sheets_client import GoogleSheetsClient
from send_intro_email import send_brine_intro_email
from scoring_agent import ScoringAgent

from maintain_leads import maintain_leads

load_dotenv()

async def run_google_maps_workflow(query: str, limit: int = 5, tab_name: str = "Sheet1", test_email: str = None):
    """
    Orchestrates the end-to-end lead generation and outreach.
    """
    # 0. Maintenance Phase (Run before discovery to handle existing funnel)
    print(f"--- STARTING MAINTENANCE ON '{tab_name}' ---")
    await maintain_leads(tab_name)
    print(f"--- MAINTENANCE COMPLETE ---")

    spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
    
    # Initialize Clients
    try:
        if not spreadsheet_id:
            print("GOOGLE_SHEETS_ID missing in .env. Creating a new spreadsheet...")
            sheets = GoogleSheetsClient()
            new_id = sheets.create_new_spreadsheet(f"Leads - {datetime.now().strftime('%Y-%m-%d')}")
            if new_id:
                print(f"PLEASE ADD THIS TO YOUR .env: GOOGLE_SHEETS_ID={new_id}")
            else:
                return
        else:
            sheets = GoogleSheetsClient(spreadsheet_id)
        
        # Initialize headers in the target tab
        sheets.initialize_sheet(tab_name)
        scorer = ScoringAgent()
    except Exception as e:
        print(f"ERROR: Could not initialize Google Sheets: {e}")
        return

    print(f"--- STARTING GOOGLE MAPS WORKFLOW ---")
    print(f"Target: {query} (Limit: {limit})")

    # 1. Scrape Google Maps
    internal_limit = limit * 5
    businesses = await scrape_google_maps(query, internal_limit)
    print(f"Initial scan found {len(businesses)} potential businesses.")

    stats = {"total": len(businesses), "synced": 0, "disqualified": 0, "contacted": 0}

    for biz in businesses:
        if stats["synced"] >= limit:
            break

        name = biz['name']
        website = biz['website']
        phone = biz['phone']
        
        # Mandatory Qualification Check: Phone
        if not phone:
            print(f"DISQUALIFIED: {name} (Missing Phone)")
            stats["disqualified"] += 1
            continue

        # 2. Extract Emails if website exists
        emails = []
        if website:
            emails = await extract_emails_from_url(website)
        
        # Mandatory Qualification Check: Email
        if not emails:
            print(f"DISQUALIFIED: {name} (Missing Email)")
            stats["disqualified"] += 1
            continue

        # 3. Fallback Naming Logic
        lead_name = f"Team at {name}" # Default fallback as per user request
        email_to_use = emails[0]

        print(f"QUALIFIED: {name} | Lead Name: {lead_name} | Email: {email_to_use}")
        
        # 3b. AI Lead Scoring
        print(f"SCORING LEAD: {name}...")
        score_data = scorer.score_lead(name, biz.get('reviews_count', 0), biz.get('rating', 0.0))
        lead_score = score_data['score']
        score_reason = score_data['reason']
        print(f"AI SCORE: {lead_score}/10 | Reason: {score_reason}")

        # 4. Sync to Google Sheets (Status: No)
        sheet_row = [
            name, 
            lead_name,
            email_to_use, 
            phone, 
            website, 
            biz['address'], 
            datetime.now().strftime("%Y-%m-%d"),
            "No", # Contacted?
            "",    # Time Contacted
            "",    # Status (Placeholder for outreach update)
            "0",   # Follow-up Count
            lead_score,
            score_reason
        ]
        
        try:
            sheets.append_leads([sheet_row], tab_name=tab_name)
            stats["synced"] += 1
            
            # 5. Automated Outreach
            recipient = test_email if test_email else email_to_use
            print(f"SENDING OUTREACH TO {recipient}...")
            
            # We determine the niche from the query if possible
            niche = query.split("in")[0].strip() if "in" in query.lower() else "your industry"
            
            email_result = send_brine_intro_email(recipient, lead_name, name, niche)
            
            if email_result['success']:
                print(f"EMAIL SENT: {name}")
                # 6. Update Sheet Status (Get row index)
                last_row = sheets.get_last_row(tab_name)
                sheets.mark_as_contacted(last_row, tab_name=tab_name)
                stats["contacted"] += 1
            else:
                print(f"EMAIL FAILED: {email_result['message']}")

        except Exception as e:
            print(f"FAILED: Processing {name}: {e}")

    print(f"--- WORKFLOW COMPLETE ---")
    print(f"Summary: Found {stats['total']}, Qualified {stats['synced']}, Contacted {stats['contacted']}, Disqualified {stats['disqualified']}")

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "Plumbing businesses in Southern California"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    tab = sys.argv[3] if len(sys.argv) > 3 else "Sheet1"
    test_email = sys.argv[4] if len(sys.argv) > 4 else None
    
    asyncio.run(run_google_maps_workflow(query, limit, tab, test_email))
