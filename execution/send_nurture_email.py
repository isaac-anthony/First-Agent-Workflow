#!/usr/bin/env python3
"""
Layer 3: Execution Script
Lead Nurture Emails (Follow-ups and 'No' Responses)
Supports threading for replies.
"""

import os
from send_onboarding_email import send_basic_email, get_env_var

DEMO_VIDEO_LINK = "https://brine.ai/demo-video"

def send_follow_up_email(lead_email: str, lead_name: str, business_name: str):
    """Sends a follow-up email after 1 week of no response."""
    company_name = get_env_var('COMPANY_NAME', default='Brine.ai')
    sender_name = get_env_var('SENDER_NAME', default='Isaac Gutierrez')
    
    subject = f"Checking in: {business_name} x {company_name}"
    
    body = f"""Hi {lead_name},

I'm checking in to see if you had a chance to read my previous email about streamlining {business_name}'s operations with AI Agents.

I'd love to have a quick 10-minute chat to see if our workflows could be a good fit for your team.

Are you free later this week?

Best regards,

{sender_name}
Founder, {company_name}
"""
    return send_basic_email(lead_email, subject, body)

def send_no_interest_email(lead_email: str, lead_name: str, thread_info: dict = None):
    """
    Sends a thank you email with a demo video when a lead is not interested.
    If thread_info is provided, it will send as a reply.
    """
    company_name = get_env_var('COMPANY_NAME', default='Brine.ai')
    sender_name = get_env_var('SENDER_NAME', default='Isaac Gutierrez')
    
    subject = "For when the timing is better + Brine.ai Demo"
    
    body = f"""Hi {lead_name},

Thank you for getting back to me. I completely understand that now might not be the right time to overhaul your workflows.

In the meantime, I’ve included a link to a brief 3-minute demo video of how our AI agents work. Feel free to take a look whenever you have a moment.

Demo Video: {DEMO_VIDEO_LINK}

If your needs change in the future, we’d love to help.

Best regards,

{sender_name}
Founder, {company_name}
"""
    
    if thread_info and 'gmail_client' in thread_info:
        gmail = thread_info['gmail_client']
        return gmail.send_reply(
            to=lead_email,
            subject=thread_info.get('subject', subject),
            body=body,
            thread_id=thread_info['thread_id'],
            in_reply_to=thread_info['message_id']
        )
    
    return send_basic_email(lead_email, subject, body)
