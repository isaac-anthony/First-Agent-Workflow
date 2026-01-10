#!/usr/bin/env python3
"""
Weekly Report Scheduler
Automatically sends weekly lead generation reports every Monday.
Can be run manually or scheduled via cron.
"""

import os
import sys
from datetime import datetime
from reporting_agent import ReportingAgent
from dotenv import load_dotenv

load_dotenv()

def should_send_weekly_report() -> bool:
    """
    Determines if we should send a weekly report.
    Sends on Mondays or if run manually.
    """
    today = datetime.now()
    # Monday is weekday 0
    return today.weekday() == 0

def send_weekly_report():
    """Sends the weekly lead generation report."""
    print("=" * 70)
    print("WEEKLY LEAD GENERATION REPORT")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        agent = ReportingAgent()
        agent.run_weekly_report()
        print("\n✅ Weekly report sent successfully!")
    except Exception as e:
        print(f"\n❌ Error sending weekly report: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Check if run manually (with --force flag) or should run automatically
    force = "--force" in sys.argv
    
    if force or should_send_weekly_report():
        send_weekly_report()
    else:
        today = datetime.now()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        print(f"Not Monday yet. Next report will be sent in {days_until_monday} days.")
        print("Run with --force to send report now.")

