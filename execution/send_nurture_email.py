#!/usr/bin/env python3
"""
Layer 3: Execution Script
Lead Nurture Emails (Multi-Stage Follow-ups and 'No' Responses)
Supports threading for all stages.
"""

import os
from send_onboarding_email import send_basic_email, get_env_var

DEMO_VIDEO_LINK = "https://brine.ai/demo-video"

def send_follow_up_stage_1(lead_email: str, lead_name: str, business_name: str, thread_info: dict = None):
    """Stage 1: Day 3 - Quick Nudge."""
    company_name = get_env_var('COMPANY_NAME', default='Brine.ai')
    sender_name = get_env_var('SENDER_NAME', default='Isaac Gutierrez')
    
    subject = f"Quick nudge: {business_name} x {company_name}"
    body = f"""Hi {lead_name},

I'm just following up to make sure my last email didn't get buried in your inbox. 

I'd still love to connect and show you how our AI agents could specifically help {business_name} scale more efficiently.

Are you open to a 10-minute chat later this week?

Best regards,

{sender_name}
Founder, {company_name}
"""
    if thread_info and 'gmail_client' in thread_info:
        return thread_info['gmail_client'].send_reply(
            to=lead_email, subject=thread_info.get('subject', subject),
            body=body, thread_id=thread_info['thread_id'], in_reply_to=thread_info['message_id']
        )
    return send_basic_email(lead_email, subject, body)

def send_follow_up_stage_2(lead_email: str, lead_name: str, business_name: str, thread_info: dict = None):
    """Stage 2: Day 7 - Value Add (Demo Video)."""
    company_name = get_env_var('COMPANY_NAME', default='Brine.ai')
    sender_name = get_env_var('SENDER_NAME', default='Isaac Gutierrez')
    
    subject = f"A quick gift for you: Brine.ai Demo"
    body = f"""Hi {lead_name},

I haven't heard back yet, so I figured I'd send over a brief 3-minute demo video of how our AI agents actually work in the wild.

Demo Video: {DEMO_VIDEO_LINK}

Most of our clients see an immediate 10-15 hour/week reduction in manual tasks after implementing these workflows.

Would this be helpful for the team at {business_name}?

Best regards,

{sender_name}
Founder, {company_name}
"""
    if thread_info and 'gmail_client' in thread_info:
        return thread_info['gmail_client'].send_reply(
            to=lead_email, subject=thread_info.get('subject', subject),
            body=body, thread_id=thread_info['thread_id'], in_reply_to=thread_info['message_id']
        )
    return send_basic_email(lead_email, subject, body)

def send_follow_up_stage_3(lead_email: str, lead_name: str, business_name: str, thread_info: dict = None):
    """Stage 3: Day 14 - The Break-up."""
    company_name = get_env_var('COMPANY_NAME', default='Brine.ai')
    sender_name = get_env_var('SENDER_NAME', default='Isaac Gutierrez')
    
    subject = f"Closing the loop: {business_name}"
    body = f"""Hi {lead_name},

I’m reaching out one last time to close the loop on this. Usually, when I don't hear back, it's either because this isn't a priority right now, or you're just too busy.

I don't want to be a bother, so I'll stop my outreach here. If your needs change in the future and you want to scale {business_name} with AI agents, feel free to reach out.

Wishing you all the best!

Best regards,

{sender_name}
Founder, {company_name}
"""
    if thread_info and 'gmail_client' in thread_info:
        return thread_info['gmail_client'].send_reply(
            to=lead_email, subject=thread_info.get('subject', subject),
            body=body, thread_id=thread_info['thread_id'], in_reply_to=thread_info['message_id']
        )
    return send_basic_email(lead_email, subject, body)

def send_welcome_back_email(lead_email: str, lead_name: str, business_name: str, thread_info: dict = None):
    """Sends a friendly follow-up after an OOO period."""
    company_name = get_env_var('COMPANY_NAME', default='Brine.ai')
    sender_name = get_env_var('SENDER_NAME', default='Isaac Gutierrez')
    
    subject = f"Welcome back! {business_name} x {company_name}"
    body = f"""Hi {lead_name},

I saw that you were out of the office recently—hope you had a great break! 

I'm bumping this to the top of your inbox now that you're back. I'd still love to connect and show you how our AI agents could specifically help {business_name} scale more efficiently.

Are you open to a brief chat later this week?

Best regards,

{sender_name}
Founder, {company_name}
"""
    if thread_info and 'gmail_client' in thread_info:
        return thread_info['gmail_client'].send_reply(
            to=lead_email, subject=thread_info.get('subject', subject),
            body=body, thread_id=thread_info['thread_id'], in_reply_to=thread_info['message_id']
        )
    return send_basic_email(lead_email, subject, body)
def send_no_interest_email(lead_email: str, lead_name: str, business_name: str = "your business", thread_info: dict = None):
    """Sends a thank you email with a demo video when a lead is not interested."""
    company_name = get_env_var('COMPANY_NAME', default='Brine.ai')
    sender_name = get_env_var('SENDER_NAME', default='Isaac Gutierrez')
    
    subject = "For when the timing is better + Brine.ai Demo"
    body = f"""Hi {lead_name},

Thank you for getting back to me. I completely understand that now might not be the right time to overhaul your workflows for {business_name}.

In the meantime, I’ve included a link to a brief 3-minute demo video of how our AI agents work. Feel free to take a look whenever you have a moment.

Demo Video: {DEMO_VIDEO_LINK}

If your needs change in the future, we’d love to help.

Best regards,

{sender_name}
Founder, {company_name}
"""
    if thread_info and 'gmail_client' in thread_info:
        return thread_info['gmail_client'].send_reply(
            to=lead_email, subject=thread_info.get('subject', subject),
            body=body, thread_id=thread_info['thread_id'], in_reply_to=thread_info['message_id']
        )
    return send_basic_email(lead_email, subject, body)
