#!/usr/bin/env python3
"""
Layer 3: Execution Script
Brine.ai Introduction Email
Sends automated outreach to qualified leads.
"""

import os
import sys
from typing import Dict
from send_onboarding_email import send_basic_email, get_env_var

def send_brine_intro_email(lead_email: str, lead_name: str, business_name: str, niche: str = "business", hook: str = None):
    """
    Sends the professional Brine.ai introduction email with an optional personalized hook.
    """
    company_name = get_env_var('COMPANY_NAME', default='Brine.ai')
    calendar_link = get_env_var('CALENDAR_LINK', default='https://calendly.com/example/kickoff-call')
    sender_name = get_env_var('SENDER_NAME', default='Isaac Gutierrez')

    subject = f"100 leads for {business_name}"
    
    # Validate and clean lead_name - if it's "Yes", empty, or invalid, use empty string
    if not lead_name or lead_name.strip().lower() in ["yes", "no", "team", ""]:
        greeting = "Hi,"
    else:
        # Extract first name if full name provided
        first_name = lead_name.strip().split()[0] if lead_name.strip() else ""
        if first_name and first_name.lower() not in ["yes", "no", "team"]:
            greeting = f"Hi {first_name},"
        else:
            greeting = "Hi,"
    
    # Use hook as opening line if it exists
    opening_line = hook if hook else f"I've been following {business_name}'s work in the {niche} space and was impressed by your local reputation."
    
    body_html = f"""
    <div style="font-family: Arial, sans-serif; font-size: 14px; color: #000000; line-height: 1.5;">
        {greeting}<br><br>
        {opening_line}<br><br>
        I’m the founder of {company_name}, and we specialize in building Agentic Workflows that automate the manual heavy lifting of prospecting and outreach for professional firms.<br><br>
        To show you the value we can bring to your team, I have a specific offer for you: I will get you 100 personalized, custom leads in one week, or you don’t pay a dime. <br><br>
        By using our proprietary discovery engine, we allow your staff to stop chasing leads and start focusing entirely on high-value advisory and serving your clients.<br><br>
        Do you have 10 minutes later this week to chat more about this?<br><br>
        Best Regards,<br><br>
        Isaac Gutierrez | Founder & Architect @ Brine.ai Consulting<br>
        brineaiconsulting.com
    </div>
    """

    return send_basic_email(lead_email, subject, body_html, is_html=True)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python send_intro_email.py <email> <name> <business_name> [niche]")
        sys.exit(1)
    
    email = sys.argv[1]
    name = sys.argv[2]
    biz = sys.argv[3]
    niche = sys.argv[4] if len(sys.argv) > 4 else "business"
    
    result = send_brine_intro_email(email, name, biz, niche)
    print(result['message'])

