#!/usr/bin/env python3
"""
Send Emails to Apollo Leads
Sends emails to the 25 most recently added Apollo leads, bypassing strict validation.
"""

import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Add execution to path
sys.path.append(os.path.dirname(__file__))

# Load .env from project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

from google_sheets_client import GoogleSheetsClient
from send_intro_email import send_brine_intro_email
from email_verifier import EmailVerifier

async def send_apollo_leads(limit: int = 25):
    """Sends emails to the most recently added Apollo leads."""
    
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
    if not spreadsheet_id:
        print("ERROR: GOOGLE_SHEETS_ID missing in .env")
        return
    
    sheets = GoogleSheetsClient(spreadsheet_id)
    verifier = EmailVerifier()
    tab_name = "Sheet2"
    
    print("=" * 70)
    print(f"SENDING EMAILS TO {limit} APOLLO LEADS")
    print("=" * 70)
    
    # Get all leads from Sheet2
    rows = sheets.get_all_values(tab_name)
    
    if not rows or len(rows) <= 1:
        print(f"No leads found in {tab_name}")
        return
    
    headers = rows[0]
    lead_rows = rows[1:]
    
    # Find column indices
    try:
        col_biz_name = headers.index("Business Name")
        col_lead_name = headers.index("Lead Name")
        col_email = headers.index("Email")
        col_contacted = headers.index("Contacted?")
        col_status = headers.index("Status")
        col_niche = headers.index("Industry") if "Industry" in headers else None
        col_hook = headers.index("Personalized Hook") if "Personalized Hook" in headers else None
        col_date_added = headers.index("Date Added") if "Date Added" in headers else None
    except ValueError as e:
        print(f"ERROR: Missing required column: {e}")
        print(f"Available columns: {headers}")
        return
    
    # Filter for leads that:
    # 1. Haven't been contacted
    # 2. Have "Pending" status (new leads ready to send)
    # Start from the END of the list (most recently added = Apollo leads)
    eligible_leads = []
    for i, row in enumerate(reversed(lead_rows), start=len(lead_rows)+1):
        # Ensure row has enough columns
        while len(row) < len(headers):
            row.append("")
        
        biz_name = row[col_biz_name].strip() if len(row) > col_biz_name else ""
        email = row[col_email].strip() if len(row) > col_email else ""
        contacted = row[col_contacted].strip().lower() if len(row) > col_contacted else ""
        status = row[col_status].strip().lower() if len(row) > col_status else ""
        
        # Only process leads that:
        # 1. Haven't been contacted
        # 2. Have "Pending" status (or empty status)
        # 3. Have valid email and business name
        if not email or not biz_name:
            continue
        
        if contacted == "yes":
            continue
        
        # Check if status is "pending" or empty (new leads)
        if status not in ["", "pending"]:
            continue
        
        eligible_leads.append((i, row))
        
        # Stop once we have enough
        if len(eligible_leads) >= limit:
            break
    
    print(f"\nFound {len(eligible_leads)} eligible leads to send emails to\n")
    
    if not eligible_leads:
        print("No eligible leads found. All leads may have already been contacted.")
        return
    
    sent_count = 0
    error_count = 0
    
    for i, row in eligible_leads:
        biz_name = row[col_biz_name].strip()
        # Extract lead_name and validate it - if it's "Yes", "No", empty, or invalid, use empty string
        raw_lead_name = row[col_lead_name].strip() if len(row) > col_lead_name and row[col_lead_name] else ""
        if raw_lead_name.lower() in ["yes", "no", "team", ""]:
            lead_name = ""
        else:
            lead_name = raw_lead_name
        email = row[col_email].strip()
        niche = row[col_niche].strip() if col_niche and len(row) > col_niche else "Business"
        hook = row[col_hook].strip() if col_hook and len(row) > col_hook else ""
        
        print(f"\n[{sent_count + 1}/{len(eligible_leads)}] Processing: {biz_name}")
        print(f"    Email: {email}")
        print(f"    Lead Name: {lead_name if lead_name else '(none - will use generic greeting)'}")
        
        # Final email verification
        v_result = verifier.verify(email)
        if not v_result['valid']:
            print(f"    ❌ SKIPPING: Email verification failed - {v_result['reason']}")
            error_count += 1
            continue
        
        # Generate hook if not present
        if not hook:
            from personalization_agent import PersonalizationAgent
            perso = PersonalizationAgent()
            hook = perso.generate_hook(f"Business: {biz_name}. Industry: {niche}.", biz_name)
            if not hook:
                hook = f"I noticed that {biz_name} has been serving the {niche} industry."
        
        # Send intro email
        print(f"    Sending intro email...")
        try:
            result = send_brine_intro_email(email, lead_name, biz_name, niche, hook=hook)
            
            if result.get('success'):
                print(f"    ✅ EMAIL SENT successfully!")
                sent_count += 1
                
                # Update sheet: Mark as contacted
                sheets.update_cell(f"Q{i}", "Yes", tab_name)  # Contacted? column (Q)
                sheets.update_cell(f"R{i}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tab_name)  # Time Contacted (R)
                sheets.update_cell(f"B{i}", "Pending", tab_name)  # Status (B)
                
                # Rate limiting: Randomized delay (10-20 seconds) to prevent blocking
                if sent_count < len(eligible_leads):
                    import random
                    delay = random.uniform(10, 20)
                    print(f"    Waiting {delay:.1f} seconds before next email (prevents blocking)...")
                    await asyncio.sleep(delay)
            else:
                print(f"    ❌ EMAIL FAILED: {result.get('message', 'Unknown error')}")
                error_count += 1
                
        except Exception as e:
            print(f"    ❌ ERROR: {str(e)}")
            error_count += 1
    
    # Final summary
    print(f"\n{'='*70}")
    print("EMAIL SENDING COMPLETE")
    print(f"{'='*70}")
    print(f"✅ Emails sent successfully: {sent_count}")
    print(f"❌ Errors: {error_count}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    asyncio.run(send_apollo_leads(limit))

