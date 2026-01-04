#!/usr/bin/env python3
"""
Layer 3: Execution Script
Notifier Agent (Hot Lead Alerts)
Sends real-time notifications to Slack when high-value actions occur.
"""

import os
import requests
import json
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class NotifierAgent:
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")

    def send_slack_message(self, message: str, blocks: list = None) -> bool:
        """Sends a message to a Slack channel via Webhook."""
        if not self.webhook_url:
            print("WARNING: SLACK_WEBHOOK_URL missing in .env. Notification skipped.")
            return False

        payload = {"text": message}
        if blocks:
            payload["blocks"] = blocks

        try:
            response = requests.post(
                self.webhook_url, 
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                return True
            else:
                print(f"Slack API Error ({response.status_code}): {response.text}")
                return False
        except Exception as e:
            print(f"Error sending Slack notification: {e}")
            return False

    def notify_hot_lead(self, biz_name: str, email: str, score: int, reason: str, description: str = ""):
        """Sends a formatted 'New High-Score Lead' alert."""
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🔥 NEW HIGH-SCORE LEAD FOUND"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Business:* \n{biz_name}"},
                    {"type": "mrkdwn", "text": f"*AI Score:* \n{score}/10"}
                ]
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*What they do:* \n{description[:300]}..." if description else "*What they do:* \nInformation not available."}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*AI Reasoning:* \n{reason}"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Contact:* {email}"}
            }
        ]
        return self.send_slack_message(f"Hot Lead: {biz_name}", blocks=blocks)

    def notify_interest(self, biz_name: str, lead_name: str, email: str, sentiment: str, message_snippet: str):
        """Sends a formatted 'Lead Replied' alert."""
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "✅ NEW LEAD INTEREST DETECTED"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Lead:* {lead_name} @ *{biz_name}*"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Sentiment:* \n{sentiment}"},
                    {"type": "mrkdwn", "text": f"*Email:* \n{email}"}
                ]
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Latest Message Snippet:* \n> {message_snippet}"}
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": "The agent has already replied with your booking link."}
                ]
            }
        ]
        return self.send_slack_message(f"Interest from: {biz_name}", blocks=blocks)

if __name__ == "__main__":
    # Test
    agent = NotifierAgent()
    # agent.notify_hot_lead("Test Firm", "test@firm.com", 9, "High volume litigation firm with 200+ reviews.")

