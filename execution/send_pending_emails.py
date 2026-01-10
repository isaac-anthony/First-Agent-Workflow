#!/usr/bin/env python3
"""
Send Pending Emails Script
Sends intro emails to all leads in Sheet2 that haven't been contacted yet.
"""

import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Add execution to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Load .env from project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

from google_sheets_client import GoogleSheetsClient
from send_intro_email import send_brine_intro_email
from personalization_agent import PersonalizationAgent
from self_healing_agent import SelfHealingAgent, validate_email_send

async def send_pending_emails():
    """Sends intro emails to all leads in Sheet2 that haven't been contacted."""
    
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
    if not spreadsheet_id:
        print("ERROR: GOOGLE_SHEETS_ID missing in .env")
        return
    
    sheets = GoogleSheetsClient(spreadsheet_id)
    perso = PersonalizationAgent()
    healer = SelfHealingAgent()  # Self-healing agent for validation
    tab_name = "Sheet2"
    
    print("=" * 70)
    print("SENDING PENDING EMAILS TO LEADS IN SHEET2")
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
        col_niche = headers.index("Industry") if "Industry" in headers else headers.index("Niche") if "Niche" in headers else None
        col_hook = headers.index("Personalized Hook") if "Personalized Hook" in headers else None
    except ValueError as e:
        print(f"ERROR: Missing required column: {e}")
        print(f"Available columns: {headers}")
        return
    
    pending_count = 0
    sent_count = 0
    error_count = 0
    
    print(f"\nFound {len(lead_rows)} total leads in Sheet2\n")
    
    for i, row in enumerate(lead_rows, start=2):
        # Ensure row has enough columns
        while len(row) < len(headers):
            row.append("")
        
        biz_name = row[col_biz_name].strip()
        # Extract lead_name and validate it - if it's "Yes", "No", empty, or invalid, use empty string
        raw_lead_name = row[col_lead_name].strip() if len(row) > col_lead_name and row[col_lead_name] else ""
        if raw_lead_name.lower() in ["yes", "no", "team", ""]:
            lead_name = ""
        else:
            lead_name = raw_lead_name
        email = row[col_email].strip()
        contacted = row[col_contacted].strip().lower() if len(row) > col_contacted else ""
        status = row[col_status].strip() if len(row) > col_status else ""
        niche = row[col_niche].strip() if col_niche and len(row) > col_niche else "Business"
        hook = row[col_hook].strip() if col_hook and len(row) > col_hook else ""
        
        # Skip if no email or business name
        if not email or not biz_name:
            print(f"SKIPPING Row {i}: Missing email or business name")
            continue
        
        # Self-Healing Agent Validation (CRITICAL: Prevents duplicates and issues)
        row_data = {
            'contacted': contacted,
            'status': status,
            'lead_name': lead_name,
            'email': email
        }
        
        is_valid, reason = healer.validate_before_send(email, lead_name, biz_name, row_data, tab_name)
        if not is_valid:
            print(f"SKIPPING {biz_name}: {reason}")
            continue
        
        # Additional manual checks (redundancy for safety)
        if contacted == "yes":
            print(f"SKIPPING {biz_name}: Already contacted (Contacted? = Yes)")
            continue
        
        # Only skip if status indicates already processed (not "pending" - that means ready to send)
        if status.lower() in ["interested", "archived", "not interested"]:
            print(f"SKIPPING {biz_name}: Status is {status}")
            continue
        
        pending_count += 1
        print(f"\n[{pending_count}] Processing: {biz_name}")
        print(f"    Email: {email}")
        print(f"    Niche: {niche}")
        
        # Generate hook if not already present
        if not hook:
            print(f"    Generating personalized hook...")
            # We need website snippet to generate hook - try to get it from sheet if available
            # For now, use business name
            hook = perso.generate_hook(f"Business: {biz_name}. Industry: {niche}.", biz_name)
            if hook:
                print(f"    Hook: {hook[:80]}...")
            else:
                hook = f"I noticed that {biz_name} has been serving the {niche} industry."
        
        # Final email verification before sending (double-check)
        from email_verifier import EmailVerifier
        verifier = EmailVerifier()
        v_result = verifier.verify(email)
        if not v_result['valid']:
            print(f"    ❌ SKIPPING: Email verification failed - {v_result['reason']}")
            error_count += 1
            continue
        
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
                
                # Update hook if we generated a new one
                if col_hook and not row[col_hook]:
                    sheets.update_cell(f"{chr(65 + col_hook)}{i}", hook, tab_name)
            else:
                print(f"    ❌ FAILED: {result.get('message', 'Unknown error')}")
                error_count += 1
        except Exception as e:
            print(f"    ❌ ERROR: {str(e)}")
            error_count += 1
        
        # Delay to avoid rate limiting - randomized to prevent detection patterns
        import random
        delay = random.uniform(10, 20)  # 10-20 seconds randomized delay
        print(f"    Waiting {delay:.1f} seconds before next email (prevents blocking)...")
        await asyncio.sleep(delay)
    
    print("\n" + "=" * 70)
    print("EMAIL SENDING COMPLETE")
    print("=" * 70)
    print(f"Total leads checked: {len(lead_rows)}")
    print(f"Pending leads found: {pending_count}")
    print(f"✅ Emails sent successfully: {sent_count}")
    print(f"❌ Errors: {error_count}")
    print(f"\nAll sent leads have been marked as 'Contacted' in Sheet2")

if __name__ == "__main__":
    asyncio.run(send_pending_emails())

