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
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
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

        my_email = os.getenv('EMAIL_FROM', 'brineaiconsulting@gmail.com').lower()
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
            # Extract email from from_header
            from_email = ""
            if from_header:
                import re
                email_match = re.search(r'<([^>]+)>', from_header)
                if email_match:
                    from_email = email_match.group(1).lower()
                elif '@' in from_header:
                    from_email = from_header.lower()
            
            return {
                "body": base64.urlsafe_b64decode(body).decode('utf-8'),
                "message_id": msg_id,
                "subject": subject,
                "thread_id": thread_id,
                "sender_name": sender_name,
                "from_email": from_email
            }
        
        return None

    def send_reply(self, to: str, subject: str, body: str, thread_id: str, in_reply_to: str, is_html: bool = False):
        """Sends an email as a reply within an existing thread."""
        try:
            import smtplib
            import time
            import random
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.utils import formataddr, formatdate
            from datetime import datetime

            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            email_from = os.getenv('EMAIL_FROM', 'brineaiconsulting@gmail.com')
            email_password = os.getenv('EMAIL_PASSWORD')
            sender_name = os.getenv('SENDER_NAME', 'Isaac Gutierrez')

            from email.utils import formatdate
            from datetime import datetime
            import time
            import random
            
            msg = MIMEMultipart()
            msg['From'] = formataddr((sender_name, email_from))
            msg['To'] = to
            msg['Subject'] = subject if subject.lower().startswith('re:') else f"Re: {subject}"
            msg['Date'] = formatdate(localtime=True)
            msg['In-Reply-To'] = in_reply_to
            msg['References'] = in_reply_to
            msg['Reply-To'] = email_from
            msg['Message-ID'] = f"<{datetime.now().timestamp()}.{hash(to)}@{email_from.split('@')[1]}>"
            msg['X-Mailer'] = 'Brine.ai Agentic Workflow'
            msg['X-Priority'] = '3'  # Normal priority
            
            mime_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(body, mime_type))
            
            # Retry logic with exponential backoff
            max_retries = 3
            retry_delay = 5
            
            for attempt in range(max_retries):
                try:
                    server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
                    server.set_debuglevel(0)  # Disable debug
                    server.starttls()
                    server.login(email_from, email_password)
                    
                    failed_recipients = server.sendmail(email_from, to, msg.as_string())
                    server.quit()
                    
                    if failed_recipients:
                        error_msg = f"Some recipients failed: {failed_recipients}"
                        self._learn_from_email_failure(to, error_msg)
                        return {"success": False, "message": error_msg}
                    
                    return {"success": True, "message": f"Reply sent to {to} in thread {thread_id}"}
                    
                except (smtplib.SMTPDataError, smtplib.SMTPServerDisconnected) as e:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        print(f"   ⚠️  Temporary error (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        error_msg = f"Gmail Error after {max_retries} attempts: {str(e)}"
                        print(f"❌ {error_msg}")
                        self._learn_from_email_failure(to, error_msg)
                        return {"success": False, "message": error_msg}
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"Gmail Authentication Error: {str(e)}"
            print(f"❌ {error_msg}")
            print("   → Check if App Password is correct and not expired")
            self._learn_from_email_failure(to, error_msg)
            return {"success": False, "message": error_msg}
        except smtplib.SMTPSenderRefused as e:
            error_msg = f"Gmail Sender Refused: {str(e)}"
            print(f"❌ {error_msg}")
            print("   → Account may be locked or daily limit exceeded (500 emails/day)")
            print("   → Check: https://myaccount.google.com/security")
            self._learn_from_email_failure(to, error_msg)
            return {"success": False, "message": error_msg}
        except smtplib.SMTPDataError as e:
            error_msg = f"Gmail Data Error: {str(e)}"
            error_code = str(e).split()[0] if str(e).split() else ""
            print(f"❌ {error_msg}")
            if "550" in error_code or "551" in error_code or "553" in error_code:
                print("   → Gmail is blocking this email (spam/security lock)")
                print("   → Account may need security verification")
            self._learn_from_email_failure(to, error_msg)
            return {"success": False, "message": error_msg}
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Email Error: {error_msg}")
            # Self-healing: Learn from email failures
            self._learn_from_email_failure(to, error_msg)
            return {"success": False, "message": f"Error sending reply: {error_msg}"}
    
    def _learn_from_email_failure(self, email: str, error: str):
        """Self-healing: Track email failures and learn from them."""
        try:
            from email_verifier import EmailVerifier
            verifier = EmailVerifier()
            
            # Check if error indicates fake/invalid email
            if any(keyword in error.lower() for keyword in ['invalid', 'not found', 'does not exist', 'no such user', '550', '551', '553']):
                verifier.learn_from_failure(email, error)
                print(f"🔒 LEARNED: Marked {email} as fake/invalid due to: {error[:100]}")
        except Exception as e:
            print(f"Warning: Could not learn from email failure: {e}")

    def create_or_get_label(self, label_name: str) -> Optional[str]:
        """Creates a Gmail label if it doesn't exist, or returns existing label ID."""
        try:
            # List all labels
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            # Check if label exists
            for label in labels:
                if label['name'] == label_name:
                    return label['id']
            
            # Create label if it doesn't exist
            label_obj = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            created = self.service.users().labels().create(userId='me', body=label_obj).execute()
            print(f"Created Gmail label: {label_name}")
            return created['id']
        except HttpError as error:
            print(f"Error creating/getting label: {error}")
            return None

    def apply_label_to_thread(self, thread_id: str, label_name: str):
        """Applies a Gmail label to all messages in a thread."""
        try:
            label_id = self.create_or_get_label(label_name)
            if label_id:
                self.service.users().threads().modify(
                    userId='me',
                    id=thread_id,
                    body={'addLabelIds': [label_id]}
                ).execute()
                print(f"Applied label '{label_name}' to thread {thread_id}")
        except HttpError as error:
            print(f"Error applying label: {error}")
