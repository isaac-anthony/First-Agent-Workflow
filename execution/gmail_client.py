#!/usr/bin/env python3
"""
Layer 3: Execution Script
Gmail Client
Handles searching for and reading email threads to detect lead responses.
"""

import os
import os.path
import base64
from typing import Optional, List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes for Gmail API
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

class GmailClient:
    def __init__(self):
        self.creds = self._authenticate()
        self.service = build('gmail', 'v1', credentials=self.creds)

    def _authenticate(self):
        creds = None
        token_path = 'token_gmail.json'
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    if os.path.exists(token_path): os.remove(token_path)
                    return self._authenticate()
            else:
                json_file = 'credentials.actual.json' if os.path.exists('credentials.actual.json') else 'credentials.json'
                if not os.path.exists(json_file):
                    raise FileNotFoundError(f"{json_file} not found.")
                
                flow = InstalledAppFlow.from_client_secrets_file(json_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        return creds

    def search_threads(self, query: str) -> List[Dict[str, Any]]:
        """Searches for threads matching the query."""
        try:
            results = self.service.users().threads().list(userId='me', q=query).execute()
            return results.get('threads', [])
        except HttpError as error:
            print(f"An error occurred searching threads: {error}")
            return []

    def get_thread_details(self, thread_id: str) -> Dict[str, Any]:
        """Retrieves details for a specific thread."""
        try:
            return self.service.users().threads().get(userId='me', id=thread_id).execute()
        except HttpError as error:
            print(f"An error occurred fetching thread details: {error}")
            return {}

    def get_full_thread_messages(self, thread_id: str) -> List[Dict[str, Any]]:
        """Retrieves all messages in a thread with basic sender/body info."""
        thread = self.get_thread_details(thread_id)
        if not thread: return []
        
        results = []
        for msg in thread.get('messages', []):
            headers = msg.get('payload', {}).get('headers', [])
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), "Unknown")
            
            # Extract body
            payload = msg.get('payload', {})
            body = ""
            
            def extract_parts(parts):
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        return part.get('body', {}).get('data', "")
                    if 'parts' in part:
                        res = extract_parts(part['parts'])
                        if res: return res
                return ""

            if 'parts' in payload:
                body = extract_parts(payload['parts'])
            else:
                body = payload.get('body', {}).get('data', "")
            
            if body:
                try:
                    decoded_body = base64.urlsafe_b64decode(body).decode('utf-8')
                except:
                    decoded_body = "[Un-decodable content]"
                
                results.append({
                    "from": sender,
                    "body": decoded_body,
                    "id": msg['id']
                })
        return results

    def get_latest_message_details(self, thread_id: str, skip_my_email: bool = True) -> Optional[Dict[str, Any]]:
        """Extracts the body and message ID of the latest message in a thread."""
        thread = self.get_thread_details(thread_id)
        if not thread: return None
        
        messages = thread.get('messages', [])
        if not messages: return None
        
        # We ALWAYS need at least 2 messages to have a reply (1 outreach + 1 reply)
        if len(messages) < 2:
            return None

        my_email = os.getenv('EMAIL_FROM', '04isaacag@gmail.com').lower()
        latest_msg = messages[-1]
        
        # In real mode, we skip if the latest message is from US.
        if skip_my_email:
            headers = latest_msg.get('payload', {}).get('headers', [])
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), "").lower()
            if my_email in sender:
                return None
        else:
            # In TEST mode (where lead and sender are the same email),
            # we only treat it as a reply if the latest message is NOT from the first message
            # AND the latest message is an ODD index (1, 3, 5...) assuming 0 is outreach.
            # This prevents the agent from replying to its own automated replies.
            if len(messages) % 2 == 0:
                # This is Message 1, 3, 5... (even number of total messages)
                # It's likely a reply from the "lead"
                pass
            else:
                # This is Message 0, 2, 4... (odd number of total messages)
                # It's likely an automated reply from the AGENT
                return None

        headers = latest_msg.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), "")
        msg_id = next((h['value'] for h in headers if h['name'].lower() == 'message-id'), "")
        from_header = next((h['value'] for h in headers if h['name'].lower() == 'from'), "")
        
        # Extract sender name from "Name <email@address.com>"
        sender_name = "Team"
        if from_header:
            import re
            name_match = re.match(r'^"?([^<"]+)"?\s*<', from_header)
            if name_match:
                sender_name = name_match.group(1).strip()
            elif '<' not in from_header:
                sender_name = from_header.strip()

        # Extract body
        payload = latest_msg.get('payload', {})
        body = ""
        
        def extract_parts(parts):
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    return part.get('body', {}).get('data', "")
                if 'parts' in part:
                    res = extract_parts(part['parts'])
                    if res: return res
            return ""

        if 'parts' in payload:
            body = extract_parts(payload['parts'])
        else:
            body = payload.get('body', {}).get('data', "")
            
        if body:
            return {
                "body": base64.urlsafe_b64decode(body).decode('utf-8'),
                "message_id": msg_id,
                "subject": subject,
                "thread_id": thread_id,
                "sender_name": sender_name
            }
        
        return None

    def send_reply(self, to: str, subject: str, body: str, thread_id: str, in_reply_to: str):
        """Sends an email as a reply within an existing thread."""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.utils import formataddr

            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            email_from = os.getenv('EMAIL_FROM', '04isaacag@gmail.com')
            email_password = os.getenv('EMAIL_PASSWORD')
            sender_name = os.getenv('SENDER_NAME', 'Isaac Gutierrez')

            msg = MIMEMultipart()
            msg['From'] = formataddr((sender_name, email_from))
            msg['To'] = to
            msg['Subject'] = subject if subject.lower().startswith('re:') else f"Re: {subject}"
            msg['In-Reply-To'] = in_reply_to
            msg['References'] = in_reply_to
            
            # Gmail specific header to ensure it threads correctly
            # Note: thread_id is usually handled by Gmail's internal processing of In-Reply-To
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_from, email_password)
            server.sendmail(email_from, to, msg.as_string())
            server.quit()
            
            return {"success": True, "message": f"Reply sent to {to} in thread {thread_id}"}
        except Exception as e:
            return {"success": False, "message": f"Error sending reply: {str(e)}"}
