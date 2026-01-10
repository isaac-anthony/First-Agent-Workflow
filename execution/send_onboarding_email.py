#!/usr/bin/env python3
"""
Send onboarding email to a new client.

Usage:
    python send_onboarding_email.py <client_email> [client_name]

Arguments:
    client_email: Email address of the client (required)
    client_name: Optional name of the client for personalization

Environment variables required:
    SMTP_SERVER, SMTP_PORT, EMAIL_FROM (defaults to brineaiconsulting@gmail.com), 
    EMAIL_PASSWORD, COMPANY_NAME, CALENDAR_LINK (defaults to example link), SENDER_NAME

Note: The email template is fixed and always produces the same professional output.
"""

import os
import sys
import smtplib
import time
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, formatdate
from datetime import datetime
import time
import random
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def validate_email(email):
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def get_env_var(var_name, required=True, default=None):
    """Get environment variable, raise error if required and missing."""
    value = os.getenv(var_name, default)
    if required and not value:
        raise ValueError(f"Missing required environment variable: {var_name}")
    return value


def format_company_background(background_text):
    """Format company background text, handling bullet points."""
    if not background_text:
        return ""
    
    # Split by newlines or pipe character
    lines = background_text.replace('|', '\n').split('\n')
    
    # Format as bullet points
    formatted_lines = []
    for line in lines:
        line = line.strip()
        if line:
            # Remove leading dash/bullet if present
            if line.startswith('- '):
                line = line[2:]
            elif line.startswith('• '):
                line = line[2:]
            formatted_lines.append(f"• {line}")
    
    return '\n'.join(formatted_lines)


from email.mime.base import MIMEBase
from email import encoders

def send_basic_email(to: str, subject: str, body: str, is_html: bool = False, attachment_path: str = None) -> dict:
    """Helper to send a basic email using SMTP, with optional attachment."""
    if not validate_email(to):
        return {"success": False, "message": f"Invalid email format: {to}"}
    
    # Check Gmail rate limits
    try:
        from gmail_rate_limiter import GmailRateLimiter
        limiter = GmailRateLimiter()
        can_send, reason = limiter.can_send()
        if not can_send:
            return {"success": False, "message": f"Gmail rate limit: {reason}"}
    except Exception as e:
        print(f"Warning: Could not check rate limits: {e}")
    
    smtp_server = get_env_var('SMTP_SERVER', default='smtp.gmail.com')
    smtp_port = int(get_env_var('SMTP_PORT', default='587'))
    email_from = get_env_var('EMAIL_FROM', default='brineaiconsulting@gmail.com')
    email_password = get_env_var('EMAIL_PASSWORD')
    sender_name = get_env_var('SENDER_NAME', default='Isaac Gutierrez')
    
    msg = MIMEMultipart()
    msg['From'] = formataddr((sender_name, email_from))
    msg['To'] = to
    msg['Subject'] = subject
    msg['Date'] = formatdate(localtime=True)
    msg['Message-ID'] = f"<{datetime.now().timestamp()}.{hash(to)}@{email_from.split('@')[1]}>"
    msg['Reply-To'] = email_from
    msg['X-Mailer'] = 'Brine.ai Agentic Workflow'
    msg['X-Priority'] = '3'  # Normal priority
    
    mime_type = 'html' if is_html else 'plain'
    msg.attach(MIMEText(body, mime_type))
    
    if attachment_path and os.path.exists(attachment_path):
        filename = os.path.basename(attachment_path)
        with open(attachment_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            msg.attach(part)
    
    # Retry logic with exponential backoff
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
            server.set_debuglevel(0)  # Disable debug to reduce noise
            server.starttls()
            server.login(email_from, email_password)
            
            # Send with proper error handling
            failed_recipients = server.sendmail(email_from, to, msg.as_string())
            server.quit()
            
            # Check if any recipients failed
            if failed_recipients:
                error_msg = f"Some recipients failed: {failed_recipients}"
                _learn_from_email_failure(to, error_msg)
                return {"success": False, "message": error_msg}
            
            # Record successful send
            try:
                from gmail_rate_limiter import GmailRateLimiter
                limiter = GmailRateLimiter()
                limiter.record_send(success=True)
            except:
                pass
            
            return {"success": True, "message": f"Email sent to {to}"}
            
        except (smtplib.SMTPDataError, smtplib.SMTPServerDisconnected) as e:
            # Temporary errors - retry with backoff
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                print(f"   ⚠️  Temporary error (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                # Final attempt failed
                error_msg = f"Gmail Error after {max_retries} attempts: {str(e)}"
                print(f"❌ {error_msg}")
                _learn_from_email_failure(to, error_msg)
                return {"success": False, "message": error_msg}
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"Gmail Authentication Error: {str(e)}"
        print(f"❌ {error_msg}")
        print("   → Check if App Password is correct and not expired")
        _learn_from_email_failure(to, error_msg)
        return {"success": False, "message": error_msg}
    except smtplib.SMTPSenderRefused as e:
        error_msg = f"Gmail Sender Refused: {str(e)}"
        print(f"❌ {error_msg}")
        print("   → Account may be locked or daily limit exceeded (500 emails/day)")
        print("   → Check: https://myaccount.google.com/security")
        _learn_from_email_failure(to, error_msg)
        return {"success": False, "message": error_msg}
    except smtplib.SMTPDataError as e:
        error_msg = f"Gmail Data Error: {str(e)}"
        error_code = str(e).split()[0] if str(e).split() else ""
        print(f"❌ {error_msg}")
        if "550" in error_code or "551" in error_code or "553" in error_code:
            print("   → Gmail is blocking this email (spam/security lock)")
            print("   → Account may need security verification")
        _learn_from_email_failure(to, error_msg)
        return {"success": False, "message": error_msg}
    except smtplib.SMTPRecipientsRefused as e:
        error_msg = f"Gmail Recipient Refused: {str(e)}"
        print(f"❌ {error_msg}")
        _learn_from_email_failure(to, error_msg)
        return {"success": False, "message": error_msg}
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Email Error: {error_msg}")
        # Self-healing: Learn from email failures
        _learn_from_email_failure(to, error_msg)
        return {"success": False, "message": f"Error: {error_msg}"}

def _learn_from_email_failure(email: str, error: str):
    """Self-healing: Track email failures and learn from them."""
    try:
        sys.path.append(os.path.dirname(__file__))
        from email_verifier import EmailVerifier
        verifier = EmailVerifier()
        
        # Check if error indicates fake/invalid email
        if any(keyword in error.lower() for keyword in ['invalid', 'not found', 'does not exist', 'no such user', '550', '551', '553', 'bounce', 'undeliverable']):
            verifier.learn_from_failure(email, error)
            print(f"🔒 LEARNED: Marked {email} as fake/invalid due to: {error[:100]}")
    except Exception as e:
        print(f"Warning: Could not learn from email failure: {e}")

def create_email_content(client_email, client_name=None, company_background=None):
    """Create the email content with fixed professional template."""
    company_name = get_env_var('COMPANY_NAME')
    calendar_link = get_env_var('CALENDAR_LINK', required=False, 
                                default='https://calendly.com/example/kickoff-call')
    sender_name = get_env_var('SENDER_NAME')
    
    # Personalize greeting
    if client_name:
        greeting = f"Hi {client_name},"
    else:
        greeting = "Hi,"
    
    # Build email body with the fixed professional template
    body = f"""{greeting}<br><br>
Thank you for choosing {company_name}! We are thrilled to have you on board and are looking forward to working with you.<br><br>
We are excited to begin incorporating our AI agents into your workflow to help your business run as efficiently as possible. Our goal is to ensure your operations are streamlined, scalable, and powered by the best agentic technology available.<br><br>
Next Steps: We'd love to schedule a kickoff call to discuss your specific needs and map out how we can best serve you. Please use the link below to book a time that works for your schedule:<br><br>
Book Your Kickoff Call Here {calendar_link}<br><br>
We're looking forward to building something great together!<br><br>
Best Regards,<br><br>
Isaac Gutierrez | Founder & Architect @ Brine.ai Consulting<br>
brineaiconsulting.com
"""
    
    body_html = f"""
    <div style="font-family: Arial, sans-serif; font-size: 14px; color: #000000; line-height: 1.5;">
        {body}
    </div>
    """
    
    return body_html


def send_onboarding_email(client_email, client_name=None, company_background=None):
    """
    Send onboarding email to client using fixed professional template.
    
    Args:
        client_email: Email address of the client
        client_name: Optional name of the client for personalization
        company_background: Deprecated - no longer used (template is fixed)
    
    Returns:
        dict with 'success' (bool) and 'message' (str)
    """
    # Validate email
    if not validate_email(client_email):
        return {
            'success': False,
            'message': f'Invalid email address format: {client_email}'
        }
    
    # Get required environment variables
    try:
        smtp_server = get_env_var('SMTP_SERVER', default='smtp.gmail.com')
        smtp_port = int(get_env_var('SMTP_PORT', default='587'))
        email_from = get_env_var('EMAIL_FROM', default='brineaiconsulting@gmail.com')
        email_password = get_env_var('EMAIL_PASSWORD')
        company_name = get_env_var('COMPANY_NAME')
        sender_name = get_env_var('SENDER_NAME')
    except ValueError as e:
        return {
            'success': False,
            'message': str(e)
        }
    
    # Create email
    msg = MIMEMultipart()
    msg['From'] = formataddr((sender_name, email_from))
    msg['To'] = client_email
    msg['Subject'] = f'Welcome to {company_name} – Let\'s get started!'
    
    # Add body (using fixed professional template)
    body_html = create_email_content(client_email, client_name)
    msg.attach(MIMEText(body_html, 'html'))
    
    # Send email
    try:
        # Use TLS
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_from, email_password)
        text = msg.as_string()
        server.sendmail(email_from, client_email, text)
        server.quit()
        
        return {
            'success': True,
            'message': f'Onboarding email sent successfully to {client_email}'
        }
    except smtplib.SMTPAuthenticationError:
        return {
            'success': False,
            'message': 'SMTP authentication failed. Check EMAIL_FROM and EMAIL_PASSWORD.'
        }
    except smtplib.SMTPException as e:
        return {
            'success': False,
            'message': f'SMTP error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Unexpected error: {str(e)}'
        }


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python send_onboarding_email.py <client_email> [client_name]")
        sys.exit(1)
    
    client_email = sys.argv[1]
    client_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = send_onboarding_email(client_email, client_name)
    
    if result['success']:
        print(result['message'])
        sys.exit(0)
    else:
        print(f"Error: {result['message']}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

