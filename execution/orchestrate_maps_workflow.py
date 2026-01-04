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
from extract_website_data import extract_website_data
from google_sheets_client import GoogleSheetsClient
from send_intro_email import send_brine_intro_email
from scoring_agent import ScoringAgent
from personalization_agent import PersonalizationAgent
from email_verifier import EmailVerifier
from notifier_agent import NotifierAgent
from maintain_leads import maintain_leads

load_dotenv()

async def process_lead(biz, niche, sheets, scorer, perso, verifier, notifier, existing_emails, test_email):
    """Processes a single business lead from start to finish."""
    name = biz['name']
    website = biz['website']
    phone = biz['phone']
    
    # Mandatory Qualification Check: Phone
    if not phone:
        print(f"DISQUALIFIED: {name} (Missing Phone)")
        return {"status": "disqualified", "reason": "Missing Phone"}

    # 2. Extract Data from Website
    emails = []
    website_snippet = ""
    if website:
        web_data = await extract_website_data(website)
        emails = web_data.get('emails', [])
        website_snippet = web_data.get('snippet', "")
    
    # 2a. Re-Discovery Loop: If no email found, trigger fallback
    if not emails:
        print(f"🔍 RE-DISCOVERY TRIGGERED: No email found for {name}. Logging for manual LinkedIn search.")
        # Future: Trigger LinkedIn scraping here
        return {"status": "disqualified", "reason": "Missing Email (Logged for Re-Discovery)"}

    # 3. Fallback Naming Logic
    lead_name = "Team" # Simplified greeting per user request
    
    # 3a. Verify Email Deliverability (The Shield)
    valid_emails = []
    for email in emails:
        v_result = verifier.verify(email)
        if v_result['valid']:
            valid_emails.append(email)
        else:
            print(f"SHIELD BLOCKED: {email} ({v_result['reason']})")
    
    if not valid_emails:
        print(f"DISQUALIFIED: {name} (No verifiable emails found)")
        return {"status": "disqualified", "reason": "Unverifiable Email"}

    email_to_use = valid_emails[0]
    
    # Deduplication Check
    if email_to_use.lower() in existing_emails:
        print(f"SKIPPING: {name} (Already in sheet)")
        return {"status": "skipped", "reason": "Duplicate"}

    print(f"QUALIFIED: {name} | Email: {email_to_use} (Verified)")
    
    # 3b. AI Lead Scoring
    print(f"SCORING LEAD: {name}...")
    score_data = scorer.score_lead(name, biz.get('reviews_count', 0), biz.get('rating', 0.0))
    lead_score = score_data['score']
    score_reason = score_data['reason']
    print(f"AI SCORE: {lead_score}/10 | Reason: {score_reason}")

    # Quality Filter: Skip leads with low scores (under 5)
    # FOR TEST MODE: Lower threshold to 1 to ensure flow is visible
    threshold = 1 if test_email else 5
    if lead_score < threshold:
        print(f"SKIPPING: {name} (Low Quality Score: {lead_score})")
        return {"status": "skipped", "reason": f"Low Score ({lead_score})"}

    # 3d. Notify if High Score (Hot Lead)
    if lead_score >= 8:
        print(f"🔥 HOT LEAD DETECTED: {name}! Sending Slack Alert...")
        notifier.notify_hot_lead(name, email_to_use, lead_score, score_reason, description=website_snippet)

    # 3c. Generate Personalized Hook
    print(f"GENERATING HOOK for {name}...")
    hook = perso.generate_hook(website_snippet, name)
    
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
        score_reason,
        hook
    ]
    
    return {
        "status": "success",
        "row": sheet_row,
        "biz_name": name,
        "email": email_to_use,
        "lead_name": lead_name,
        "hook": hook
    }

async def run_campaign(target: dict, sheets: GoogleSheetsClient, scorer: ScoringAgent, perso: PersonalizationAgent, verifier: EmailVerifier, notifier: NotifierAgent, test_email: str = None):
    """
    Executes a single campaign for a specific niche and location using ASYNCHRONOUS processing.
    """
    niche = target['niche']
    location = target['location']
    limit = target.get('limit', 5)
    query = f"{niche} in {location}"
    tab_name = niche.replace(' ', '_').replace('&', 'n')
    
    print(f"\n--- STARTING CAMPAIGN: {query} (ASYNCHRONOUS) ---")
    sheets.initialize_sheet(tab_name)
    
    existing_rows = sheets.get_all_values(tab_name)
    existing_emails = set()
    if len(existing_rows) > 1:
        try:
            email_idx = existing_rows[0].index("Email")
            existing_emails = {row[email_idx].lower() for row in existing_rows[1:] if len(row) > email_idx}
        except ValueError: pass

    # 1. Discovery
    internal_limit = limit * 5
    businesses = await scrape_google_maps(query, internal_limit)
    print(f"Initial scan found {len(businesses)} potential businesses.")

    # 2. Parallel Processing in batches of 5
    stats = {"total": len(businesses), "synced": 0, "disqualified": 0, "contacted": 0}
    batch_size = 5
    
    for i in range(0, len(businesses), batch_size):
        if stats["synced"] >= limit: break
        
        batch = businesses[i:i+batch_size]
        print(f"\nProcessing batch {i//batch_size + 1} ({len(batch)} businesses)...")
        
        tasks = [
            process_lead(biz, niche, sheets, scorer, perso, verifier, notifier, existing_emails, test_email)
            for biz in batch
        ]
        
        results = await asyncio.gather(*tasks)
        
        for res in results:
            if stats["synced"] >= limit: break
            
            if res["status"] == "success":
                try:
                    sheets.append_leads([res["row"]], tab_name=tab_name)
                    stats["synced"] += 1
                    
                    # Outreach
                    recipient = test_email if test_email else res["email"]
                    print(f"SENDING OUTREACH TO {recipient}...")
                    
                    email_result = send_brine_intro_email(recipient, res["lead_name"], res["biz_name"], niche, hook=res["hook"])
                    if email_result['success']:
                        print(f"EMAIL SENT: {res['biz_name']}")
                        last_row = sheets.get_last_row(tab_name)
                        sheets.mark_as_contacted(last_row, tab_name=tab_name)
                        stats["contacted"] += 1
                except Exception as e:
                    print(f"Error syncing lead: {e}")
            elif res["status"] == "disqualified":
                stats["disqualified"] += 1

    print(f"--- CAMPAIGN {query} COMPLETE ---")
    return stats

    print(f"--- CAMPAIGN {query} COMPLETE ---")
    return stats

async def run_multi_niche_workflow(config_path: str, test_email: str = None):
    """
    Main orchestrator for multiple niches and maintenance.
    """
    # Load targets
    try:
        if config_path.endswith(".json"):
            with open(config_path, 'r') as f:
                targets = json.load(f)
        else:
            # Assume it's a single query string for backward compatibility
            targets = [{"niche": config_path, "location": "your area", "limit": 5}]
    except Exception as e:
        print(f"ERROR: Could not load targets: {e}")
        return

    spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
    if not spreadsheet_id:
        print("ERROR: GOOGLE_SHEETS_ID missing.")
        return

    sheets = GoogleSheetsClient(spreadsheet_id)
    scorer = ScoringAgent()
    perso = PersonalizationAgent()
    verifier = EmailVerifier()
    notifier = NotifierAgent()

    # 0. Maintenance Phase
    print("--- STARTING GLOBAL MAINTENANCE ---")
    for target in targets:
        tab_name = target['niche'].replace(' ', '_').replace('&', 'n')
        try:
            await maintain_leads(tab_name, is_test=(test_email is not None))
        except Exception as e:
            print(f"Maintenance failed for {tab_name}: {e}")
    print("--- GLOBAL MAINTENANCE COMPLETE ---")

    # 1. Discovery & Outreach Phase
    for target in targets:
        await run_campaign(target, sheets, scorer, perso, verifier, notifier, test_email)

    print("\n--- ALL CAMPAIGNS COMPLETE ---")

if __name__ == "__main__":
    # Usage: python3 orchestrate_maps_workflow.py [config.json OR niche_query] [test_email]
    arg1 = sys.argv[1] if len(sys.argv) > 1 else "config/targets.json"
    test_mode_email = sys.argv[2] if len(sys.argv) > 2 else None
    
    asyncio.run(run_multi_niche_workflow(arg1, test_mode_email))
