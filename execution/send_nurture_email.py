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
    
    subject = f"Re: 100 leads for {business_name}"
    body_html = f"""
    <div style="font-family: Arial, sans-serif; font-size: 14px; color: #000000; line-height: 1.5;">
        Hi {lead_name},<br><br>
        I'm just bumping this to the top of your inbox to make sure you saw my last note.<br><br>
        As I mentioned, I want to prove the value of our AI workflows to {business_name} by taking the prospecting off your plate. I will get you 100 personalized, custom leads in one week, or you don't pay a dime.<br><br>
        I have an engine already built waiting for you. If you want to give me some industries or leads you would like to gain, let me know and I can show you on a quick call.<br><br>
        Do you have 10 minutes later this week to chat more about this?<br><br>
        Best Regards,<br><br>
        Isaac Gutierrez | Founder & Architect @ Brine.ai Consulting<br>
        brineaiconsulting.com
    </div>
    """
    if thread_info and 'gmail_client' in thread_info:
        return thread_info['gmail_client'].send_reply(
            to=lead_email, subject=thread_info.get('subject', subject),
            body=body_html, thread_id=thread_info['thread_id'], in_reply_to=thread_info['message_id'],
            is_html=True
        )
    return send_basic_email(lead_email, subject, body_html, is_html=True)

def send_follow_up_stage_2(lead_email: str, lead_name: str, business_name: str, thread_info: dict = None):
    """Stage 2: Day 7 - Value Add."""
    company_name = get_env_var('COMPANY_NAME', default='Brine.ai')
    sender_name = get_env_var('SENDER_NAME', default='Isaac Gutierrez')
    
    subject = f"Re: 100 leads for {business_name}"
    body_html = f"""
    <div style="font-family: Arial, sans-serif; font-size: 14px; color: #000000; line-height: 1.5;">
        Hi {lead_name},<br><br>
        I'm following up one more time to see if you're still interested in getting those 100 personalized leads for {business_name}.<br><br>
        I will get you 100 qualified leads in one week, custom-tailored to your criteria, or you don't pay. Our custom workflows can save you significant time and money by automating your prospecting.<br><br>
        I have an engine already built waiting for you. If you want to give me some industries or leads you would like to gain, let me know and I can show you on a quick call.<br><br>
        Do you have 10 minutes later this week to chat more about this?<br><br>
        Best Regards,<br><br>
        Isaac Gutierrez | Founder & Architect @ Brine.ai Consulting<br>
        brineaiconsulting.com
    </div>
    """
    if thread_info and 'gmail_client' in thread_info:
        return thread_info['gmail_client'].send_reply(
            to=lead_email, subject=thread_info.get('subject', subject),
            body=body_html, thread_id=thread_info['thread_id'], in_reply_to=thread_info['message_id'],
            is_html=True
        )
    return send_basic_email(lead_email, subject, body_html, is_html=True)

def send_follow_up_stage_3(lead_email: str, lead_name: str, business_name: str, thread_info: dict = None):
    """Stage 3: Day 14 - The Break-up."""
    company_name = get_env_var('COMPANY_NAME', default='Brine.ai')
    sender_name = get_env_var('SENDER_NAME', default='Isaac Gutierrez')
    
    subject = f"Re: 100 leads for {business_name}"
    body_html = f"""
    <div style="font-family: Arial, sans-serif; font-size: 14px; color: #000000; line-height: 1.5;">
        Hi {lead_name},<br><br>
        I'm reaching out one last time regarding the automation of {business_name}'s lead gen.<br><br>
        Usually, when I don't hear back, it means priorities have shifted or the timing isn't right. I'm cleaning up my active pipeline this week—do I have your permission to close your file?<br><br>
        If you're still interested in those 100 leads but just been swamped, let me know. Otherwise, I'll stop my outreach here and wish you the best for 2026.<br><br>
        Best Regards,<br><br>
        Isaac Gutierrez | Founder & Architect @ Brine.ai Consulting<br>
        brineaiconsulting.com
    </div>
    """
    if thread_info and 'gmail_client' in thread_info:
        return thread_info['gmail_client'].send_reply(
            to=lead_email, subject=thread_info.get('subject', subject),
            body=body_html, thread_id=thread_info['thread_id'], in_reply_to=thread_info['message_id'],
            is_html=True
        )
    return send_basic_email(lead_email, subject, body_html, is_html=True)

def send_welcome_back_email(lead_email: str, lead_name: str, business_name: str, thread_info: dict = None):
    """Sends a friendly follow-up after an OOO period."""
    company_name = get_env_var('COMPANY_NAME', default='Brine.ai')
    sender_name = get_env_var('SENDER_NAME', default='Isaac Gutierrez')
    
    subject = f"Welcome back! {business_name} x {company_name}"
    body_html = f"""
    <div style="font-family: Arial, sans-serif; font-size: 14px; color: #000000; line-height: 1.5;">
        Hi {lead_name},<br><br>
        I saw that you were out of the office recently—hope you had a great break! <br><br>
        I'm bumping this to the top of your inbox now that you're back. I'd still love to connect and show you how our AI agents could specifically help {business_name} scale more efficiently.<br><br>
        Are you open to a brief chat later this week?<br><br>
        Best Regards,<br><br>
        Isaac Gutierrez | Founder & Architect @ Brine.ai Consulting<br>
        brineaiconsulting.com
    </div>
    """
    if thread_info and 'gmail_client' in thread_info:
        return thread_info['gmail_client'].send_reply(
            to=lead_email, subject=thread_info.get('subject', subject),
            body=body_html, thread_id=thread_info['thread_id'], in_reply_to=thread_info['message_id'],
            is_html=True
        )
    return send_basic_email(lead_email, subject, body_html, is_html=True)
def send_no_interest_email(lead_email: str, lead_name: str, business_name: str = "your business", thread_info: dict = None):
    """Sends a thank you email when a lead is not interested."""
    company_name = get_env_var('COMPANY_NAME', default='Brine.ai')
    sender_name = get_env_var('SENDER_NAME', default='Isaac Gutierrez')
    
    subject = f"Re: 100 leads for {business_name}"
    body_html = f"""
    <div style="font-family: Arial, sans-serif; font-size: 14px; color: #000000; line-height: 1.5;">
        Hi {lead_name},<br><br>
        No worries at all. I completely understand that now might not be the right time.<br><br>
        Just to keep Brine.ai in mind for the future: we specialize in creating custom workflows that automate your prospecting and outreach, saving you significant time and money. Our AI agents can handle the heavy lifting so your team can focus on what matters most.<br><br>
        If your needs change down the road, we'd love to help you scale {business_name} with automation.<br><br>
        Best Regards,<br><br>
        Isaac Gutierrez | Founder & Architect @ Brine.ai Consulting<br>
        brineaiconsulting.com
    </div>
    """
    if thread_info and 'gmail_client' in thread_info:
        return thread_info['gmail_client'].send_reply(
            to=lead_email, subject=thread_info.get('subject', subject),
            body=body_html, thread_id=thread_info['thread_id'], in_reply_to=thread_info['message_id'],
            is_html=True
        )
    return send_basic_email(lead_email, subject, body_html, is_html=True)
