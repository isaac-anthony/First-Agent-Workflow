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

    subject = f"Streamlining {business_name}'s operations with AI Agents"
    
    # Use hook as opening line if it exists
    opening_line = hook if hook else f"I noticed {business_name} while looking at successful businesses in the {niche} space."
    
    body = f"""Hi {lead_name},

{opening_line}

I’m reaching out from {company_name}. We specialize in building Agentic Workflows that add AI Agents into your business to significantly increase efficiency and scale your operations.

I'd love to show you how we can automate some of your manual processes. Are you available for a brief kickoff call?

Book Your Call Here: {calendar_link}

Best regards,

{sender_name}
Founder, {company_name}
"""

    return send_basic_email(lead_email, subject, body)

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

