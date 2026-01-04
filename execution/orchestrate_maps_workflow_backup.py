#!/usr/bin/env python3
"""
Layer 2: Orchestration Script
Google Maps Small Business Workflow
Integrates scraping, extraction, Google Sheets, and Automated Outreach.
Updated to support multi-niche campaigns and automated tab management.
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

async def run_campaign(target: dict, sheets: GoogleSheetsClient, scorer: ScoringAgent, test_email: str = None):
    """
    Executes a single campaign for a specific niche and location.
    """
    niche = target['niche']
    location = target['location']
    limit = target.get('limit', 5)
    query = f"{niche} in {location}"
    tab_name = f"{niche.replace(' ', '_')}_{location.split()[0]}"
    
    print(f"\n--- STARTING CAMPAIGN: {query} ---")
    
    # Initialize headers in the target tab
    sheets.initialize_sheet(tab_name)
    
    # 1. Scrape Google Maps
    internal_limit = limit * 5
    businesses = await scrape_google_maps(query, internal_limit)
    print(f"Initial scan for {query} found {len(businesses)} potential businesses.")

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
        lead_name = f"Team at {name}"
        email_to_use = emails[0]

        print(f"QUALIFIED: {name} | Email: {email_to_use}")
        
        # 3b. AI Lead Scoring
        print(f"SCORING LEAD: {name}...")
        score_data = scorer.score_lead(name, biz.get('reviews_count', 0), biz.get('rating', 0.0))
        lead_score = score_data['score']
        score_reason = score_data['reason']
        print(f"AI SCORE: {lead_score}/10 | Reason: {score_reason}")

        # 4. Sync to Google Sheets
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
            "",    # Status
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
            
            email_result = send_brine_intro_email(recipient, lead_name, name, niche)
            
            if email_result['success']:
                print(f"EMAIL SENT: {name}")
                last_row = sheets.get_last_row(tab_name)
                sheets.mark_as_contacted(last_row, tab_name=tab_name)
                stats["contacted"] += 1
            else:
                print(f"EMAIL FAILED: {email_result['message']}")

        except Exception as e:
            print(f"FAILED: Processing {name}: {e}")

    print(f"--- CAMPAIGN {query} COMPLETE ---")
    return stats

async def run_multi_niche_workflow(config_path: str, test_email: str = None):
    """
    Main orchestrator for multiple niches and maintenance.
    """
    # Load targets
    try:
        with open(config_path, 'r') as f:
            targets = json.load(f)
    except Exception as e:
        print(f"ERROR: Could not load config from {config_path}: {e}")
        return

    spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
    if not spreadsheet_id:
        print("ERROR: GOOGLE_SHEETS_ID missing.")
        return

    sheets = GoogleSheetsClient(spreadsheet_id)
    scorer = ScoringAgent()

    # 0. Maintenance Phase (Run once for all existing tabs)
    print("--- STARTING GLOBAL MAINTENANCE ---")
    # For simplicity, we maintain the tabs defined in our config
    for target in targets:
        tab_name = f"{target['niche'].replace(' ', '_')}_{target['location'].split()[0]}"
        await maintain_leads(tab_name, is_test=(test_email is not None))
    print("--- GLOBAL MAINTENANCE COMPLETE ---")

    # 1. Discovery & Outreach Phase
    all_stats = []
    for target in targets:
        stats = await run_campaign(target, sheets, scorer, test_email)
        all_stats.append(stats)

    print("\n--- ALL CAMPAIGNS COMPLETE ---")

if __name__ == "__main__":
    # If a config file is provided as the first argument, run multi-niche
    # Otherwise, fallback to single search for backward compatibility
    arg1 = sys.argv[1] if len(sys.argv) > 1 else "config/targets.json"
    
    if arg1.endswith(".json"):
        test_mode_email = sys.argv[2] if len(sys.argv) > 2 else None
        asyncio.run(run_multi_niche_workflow(arg1, test_mode_email))
    else:
        # Fallback to original single search logic (for manual terminal runs)
        # This keeps the original functionality intact
        from orchestrate_maps_workflow_legacy import run_google_maps_workflow_legacy
        query = arg1
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        tab = sys.argv[3] if len(sys.argv) > 3 else "Sheet1"
        test_email = sys.argv[4] if len(sys.argv) > 4 else None
        asyncio.run(run_google_maps_workflow_legacy(query, limit, tab, test_email))
