#!/usr/bin/env python3
"""
Test script to send examples of all Brine.ai email templates.
Target: 04isaacag@gmail.com
"""

import os
import sys
from dotenv import load_dotenv

# Add execution to path
sys.path.append(os.path.join(os.getcwd(), 'execution'))

from send_intro_email import send_brine_intro_email
from send_nurture_email import send_follow_up_stage_1, send_follow_up_stage_2, send_follow_up_stage_3, send_no_interest_email
from send_interested_email import send_interested_reply

load_dotenv()

def run_email_test():
    recipient = "04isaacag@gmail.com"
    lead_name = "Team"
    biz_name = "Test Business Corp"
    niche = "Small Business"
    
    print(f"--- SENDING TEST EMAILS TO {recipient} ---")

    # 1. Intro Email
    print("1. Sending Intro Email...")
    send_brine_intro_email(recipient, lead_name, biz_name, niche, hook="I noticed you recently won the Small Business Excellence award!")

    # 2. Stage 1 Follow-up
    print("2. Sending Stage 1 Follow-up (Day 3)...")
    send_follow_up_stage_1(recipient, lead_name, biz_name)

    # 3. Stage 2 Follow-up
    print("3. Sending Stage 2 Follow-up (Day 7)...")
    send_follow_up_stage_2(recipient, lead_name, biz_name)

    # 4. Stage 3 Follow-up
    print("4. Sending Stage 3 Follow-up (Day 14)...")
    send_follow_up_stage_3(recipient, lead_name, biz_name)

    # 5. Interested Reply
    print("5. Sending Interested Reply (with Booking Link)...")
    send_interested_reply(recipient, lead_name)

    # 6. No Interest Reply
    print("6. Sending No Interest Reply (with Demo Video)...")
    send_no_interest_email(recipient, lead_name)

    print("\n--- TEST COMPLETE ---")
    print("Check your inbox for 6 new test emails.")

if __name__ == "__main__":
    run_email_test()

