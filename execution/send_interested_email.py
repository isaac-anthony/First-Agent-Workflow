#!/usr/bin/env python3
"""
Layer 3: Execution Script
Interested Lead Responses (Scheduling Emails)
Supports threading for replies.
"""

import os
from send_onboarding_email import send_basic_email, get_env_var

BOOKING_LINK = "https://calendly.com/brine-ai/demo" # Replace with actual booking link

def send_interested_reply(lead_email: str, lead_name: str, thread_info: dict = None, custom_body: str = None):
    """
    Sends a thank you email with a booking link when a lead expresses interest.
    If thread_info is provided, it will send as a reply.
    """
    company_name = get_env_var('COMPANY_NAME', default='Brine.ai')
    sender_name = get_env_var('SENDER_NAME', default='Isaac Gutierrez')
    
    subject = f"Next Steps: Brine.ai x {lead_name}"
    
    body = custom_body or f"""Hi {lead_name},

That's great to hear! I'm thrilled you're interested in learning more about how Brine.ai can help scale your operations with AI agents.

To make things easy, here is a link to my calendar where you can grab a 15-minute slot that works best for you:

Book Your Demo Here: {BOOKING_LINK}

I'm looking forward to speaking with you and showing you what we can do!

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

