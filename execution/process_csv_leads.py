#!/usr/bin/env python3
"""
Process CSV Leads Script
Reads leads from a CSV file, processes them through the full pipeline,
and adds them to Sheet2 (same format as Google Maps leads).
"""

import os
import sys
import csv
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# Add execution to path
sys.path.append(os.path.dirname(__file__))

from google_sheets_client import GoogleSheetsClient
from scoring_agent import ScoringAgent
from personalization_agent import PersonalizationAgent
from email_verifier import EmailVerifier
from extract_website_data import extract_website_data
from notifier_agent import NotifierAgent
from self_healing_agent import SelfHealingAgent

load_dotenv()

async def process_csv_lead(row: Dict[str, str], scorer: ScoringAgent, perso: PersonalizationAgent, 
                          verifier: EmailVerifier, notifier: NotifierAgent, existing_emails: set, bypass_score: bool = False) -> Dict[str, Any]:
    """
    Processes a single lead from CSV through the full pipeline.
    Returns the formatted row data for Sheet2.
    """
    # Extract data from CSV row (flexible column names - handles Apollo format)
    biz_name = row.get('Company Name') or row.get('Business Name') or row.get('business_name') or row.get('Company') or row.get('company') or ""
    email = row.get('Email') or row.get('email') or ""
    website = row.get('Website') or row.get('website') or row.get('URL') or row.get('url') or row.get('Company Website') or ""
    phone = row.get('Work Direct Phone') or row.get('Corporate Phone') or row.get('Phone') or row.get('phone') or ""
    niche = row.get('Industry') or row.get('industry') or row.get('Niche') or row.get('niche') or "Business"
    # Handle Apollo format: First Name + Last Name
    first_name = row.get('First Name') or row.get('first_name') or ""
    last_name = row.get('Last Name') or row.get('last_name') or ""
    if first_name and last_name:
        lead_name = f"{first_name} {last_name}"
    elif first_name:
        lead_name = first_name
    else:
        # Get lead name from other columns, but validate it
        raw_lead_name = row.get('Lead Name') or row.get('lead_name') or row.get('Name') or row.get('name') or ""
        if raw_lead_name.lower() in ["yes", "no", "team", ""]:
            lead_name = ""
        else:
            lead_name = raw_lead_name
    reviews_count = int(row.get('Review Count', 0) or row.get('review_count', 0) or 0)
    rating = float(row.get('Rating', 0) or row.get('rating', 0) or 0.0)
    
    # Mandatory checks
    if not biz_name:
        print(f"SKIPPING: Missing Business Name")
        return {"status": "skipped", "reason": "Missing Business Name"}
    
    if not email:
        print(f"SKIPPING {biz_name}: Missing Email")
        return {"status": "skipped", "reason": "Missing Email"}
    
    # Verify email (but user said emails are already verified, so we'll still check but be lenient)
    v_result = verifier.verify(email)
    if not v_result['valid']:
        print(f"SHIELD BLOCKED {biz_name}: {email} ({v_result['reason']})")
        # Since user said emails are verified, we'll still proceed but log the warning
        # return {"status": "skipped", "reason": f"Invalid Email: {v_result['reason']}"}
    
    # Check for duplicates
    if email.lower() in existing_emails:
        print(f"SKIPPING {biz_name}: Duplicate email")
        return {"status": "skipped", "reason": "Duplicate"}
    
    # Extract website data if website provided
    website_snippet = ""
    automation_gaps = []
    social = {"linkedin": "", "facebook": "", "instagram": ""}
    
    if website:
        print(f"EXTRACTING DATA from {website}...")
        try:
            web_data = await extract_website_data(website)
            website_snippet = web_data.get('snippet', "")
            automation_gaps = web_data.get('automation_gaps', [])
            social = web_data.get('social', social)
            
            # If CSV didn't have email but website extraction found one, use it
            if not email and web_data.get('emails'):
                valid_emails = [e for e in web_data['emails'] if verifier.verify(e)['valid']]
                if valid_emails:
                    email = valid_emails[0]
                    print(f"FOUND EMAIL from website: {email}")
        except Exception as e:
            print(f"Error extracting website data: {e}")
    
    # Score the lead
    print(f"SCORING LEAD: {biz_name}...")
    score_data = scorer.score_lead(
        biz_name, 
        reviews_count, 
        rating, 
        markdown_dna=website_snippet, 
        automation_gaps=automation_gaps
    )
    lead_score = score_data['score']
    score_reason = score_data['reason']
    if automation_gaps:
        score_reason = f"Gaps: {', '.join(automation_gaps)} | {score_reason}"
    print(f"AI SCORE: {lead_score}/10 | Reason: {score_reason}")
    
    # Quality filter: Skip low scores (under 5) - unless bypass_score is True
    if not bypass_score and lead_score < 5:
        print(f"SKIPPING {biz_name}: Low Quality Score ({lead_score})")
        return {"status": "skipped", "reason": f"Low Score ({lead_score})"}
    
    # Notify if high score
    if lead_score >= 8:
        print(f"🔥 HOT LEAD DETECTED: {biz_name}! Sending Slack Alert...")
        notifier.notify_hot_lead(biz_name, email, lead_score, score_reason, description=website_snippet)
    
    # Generate personalized hook
    print(f"GENERATING HOOK for {biz_name}...")
    hook = perso.generate_hook(website_snippet, biz_name) if website_snippet else ""
    
    # Format row for Sheet2 (matching orchestrate_maps_workflow.py format)
    sheet_row = [
        datetime.now().strftime("%Y-%m-%d"),  # Date Added
        "Pending",                             # Status
        "",                                    # Years in Business
        biz_name,                              # Business Name
        niche,                                 # Industry
        lead_score,                            # Lead Score
        score_reason,                          # Description
        email,                                 # Email
        phone,                                 # Phone
        social.get("linkedin", ""),            # LinkedIn
        social.get("facebook", ""),            # Facebook
        social.get("instagram", ""),           # Instagram
        reviews_count,                         # Review Count
        hook,                                  # Personalized Hook
        website,                               # Website
        lead_name,                             # Lead Name
        "No",                                  # Contacted?
        "",                                    # Time Contacted
        "0"                                    # Follow-up Count
    ]
    
    print(f"✅ QUALIFIED: {biz_name} | Email: {email} | Score: {lead_score}/10")
    
    return {
        "status": "success",
        "row": sheet_row,
        "biz_name": biz_name,
        "email": email,
        "lead_name": lead_name,
        "hook": hook
    }

async def process_csv_file(csv_path: str, tab_name: str = "Sheet2", limit: int = None, test_mode: bool = False, bypass_score: bool = False):
    """
    Main function to process CSV file and add leads to Sheet2.
    """
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
    if not spreadsheet_id:
        print("ERROR: GOOGLE_SHEETS_ID missing in .env")
        return
    
    # Initialize agents
    sheets = GoogleSheetsClient(spreadsheet_id)
    scorer = ScoringAgent()
    perso = PersonalizationAgent()
    verifier = EmailVerifier()
    notifier = NotifierAgent()
    healer = SelfHealingAgent()
    
    # Ensure Sheet2 exists and has headers
    sheets.initialize_sheet(tab_name)
    
    # Get existing emails to prevent duplicates
    existing_rows = sheets.get_all_values(tab_name)
    existing_emails = set()
    if existing_rows and len(existing_rows) > 1:
        headers = existing_rows[0]
        try:
            email_col = headers.index("Email")
            for row in existing_rows[1:]:
                if len(row) > email_col and row[email_col]:
                    existing_emails.add(row[email_col].lower())
        except ValueError:
            pass
    
    print(f"Found {len(existing_emails)} existing leads in {tab_name}")
    
    # Read CSV file
    print(f"\nReading CSV file: {csv_path}")
    leads = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append(row)
    
    # Limit to first N leads if specified
    if limit:
        leads = leads[:limit]
        print(f"Processing first {limit} leads from CSV\n")
    else:
        print(f"Found {len(leads)} leads in CSV\n")
    
    # Process leads in batches
    batch_size = 5
    stats = {"processed": 0, "synced": 0, "skipped": 0, "errors": 0}
    
    for i in range(0, len(leads), batch_size):
        batch = leads[i:i+batch_size]
        print(f"\n{'='*70}")
        print(f"Processing batch {i//batch_size + 1} ({len(batch)} leads)...")
        print(f"{'='*70}\n")
        
        tasks = [
            process_csv_lead(lead, scorer, perso, verifier, notifier, existing_emails, bypass_score)
            for lead in batch
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in results:
            stats["processed"] += 1
            
            if isinstance(res, Exception):
                print(f"ERROR: {res}")
                stats["errors"] += 1
                continue
            
            if res["status"] == "success":
                try:
                    # For CSV imports, we only check for duplicate emails (already done above)
                    # Skip validation since these are new leads being added, not emails being sent
                    
                    # Add to sheet
                    sheets.append_leads([res["row"]], tab_name=tab_name)
                    existing_emails.add(res["email"].lower())  # Track added email
                    stats["synced"] += 1
                    print(f"✅ ADDED TO SHEET2: {res['biz_name']}")
                    
                    # Rate limiting (5 seconds between batches)
                    if not test_mode:
                        await asyncio.sleep(5)
                        
                except Exception as e:
                    print(f"ERROR adding {res.get('biz_name', 'unknown')} to sheet: {e}")
                    stats["errors"] += 1
            else:
                stats["skipped"] += 1
    
    # Final summary
    print(f"\n{'='*70}")
    print("CSV PROCESSING COMPLETE")
    print(f"{'='*70}")
    print(f"Total Processed: {stats['processed']}")
    print(f"✅ Synced to Sheet2: {stats['synced']}")
    print(f"⏭️  Skipped: {stats['skipped']}")
    print(f"❌ Errors: {stats['errors']}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 process_csv_leads.py <csv_file_path> [tab_name] [--limit N] [--test]")
        print("\nExample:")
        print("  python3 process_csv_leads.py leads.csv Sheet2")
        print("  python3 process_csv_leads.py leads.csv Sheet2 --limit 25")
        print("  python3 process_csv_leads.py leads.csv Sheet2 --limit 25 --test")
        print("\nCSV Format (flexible column names):")
        print("  Required: Business Name (or Company), Email")
        print("  Optional: Website, Phone, Industry, Lead Name, Review Count, Rating")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    tab_name = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else "Sheet2"
    
    # Parse arguments
    limit = None
    test_mode = False
    bypass_score = False
    for arg in sys.argv[2:]:
        if arg.startswith('--limit'):
            try:
                limit = int(sys.argv[sys.argv.index(arg) + 1])
            except (ValueError, IndexError):
                print("ERROR: --limit requires a number")
                sys.exit(1)
        elif arg == '--test':
            test_mode = True
        elif arg == '--bypass-score':
            bypass_score = True
    
    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found: {csv_path}")
        sys.exit(1)
    
    asyncio.run(process_csv_file(csv_path, tab_name, limit, test_mode, bypass_score))

