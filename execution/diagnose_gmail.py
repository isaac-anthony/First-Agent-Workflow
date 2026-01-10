#!/usr/bin/env python3
"""
Gmail Diagnostic Tool
Checks Gmail account status and email sending capabilities.
"""

import os
import sys
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

# Load .env
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

def test_gmail_connection():
    """Tests Gmail SMTP connection and authentication."""
    print("=" * 70)
    print("GMAIL DIAGNOSTIC TOOL")
    print("=" * 70)
    
    email_from = os.getenv('EMAIL_FROM', 'brineaiconsulting@gmail.com')
    email_password = os.getenv('EMAIL_PASSWORD')
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    
    print(f"\n📧 Email Account: {email_from}")
    print(f"🔐 Has Password: {'Yes' if email_password else 'No'}")
    print(f"🌐 SMTP Server: {smtp_server}:{smtp_port}")
    
    if not email_password:
        print("\n❌ ERROR: EMAIL_PASSWORD not found in .env")
        print("   Please add your Gmail App Password to .env")
        return False
    
    # Test connection
    print("\n🔍 Testing SMTP Connection...")
    try:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.set_debuglevel(1)  # Enable debug output
        print("   ✓ Connected to SMTP server")
        
        print("\n🔐 Testing Authentication...")
        server.starttls()
        print("   ✓ TLS started")
        
        server.login(email_from, email_password)
        print("   ✓ Authentication successful")
        
        # Test sending a small email to yourself
        print("\n📤 Testing Email Send (to yourself)...")
        test_msg = MIMEMultipart()
        test_msg['From'] = formataddr(("Test", email_from))
        test_msg['To'] = email_from
        test_msg['Subject'] = "Gmail Diagnostic Test"
        test_msg.attach(MIMEText("This is a test email to verify Gmail is working.", 'plain'))
        
        server.sendmail(email_from, email_from, test_msg.as_string())
        print("   ✓ Test email sent successfully!")
        
        server.quit()
        print("\n✅ Gmail is working correctly!")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ AUTHENTICATION ERROR: {e}")
        print("\nPossible causes:")
        print("  1. App Password is incorrect or expired")
        print("  2. 2-Factor Authentication is not enabled")
        print("  3. 'Less secure app access' needs to be enabled")
        print("\nFix:")
        print("  1. Go to: https://myaccount.google.com/apppasswords")
        print("  2. Generate a new App Password")
        print("  3. Update EMAIL_PASSWORD in .env")
        return False
        
    except smtplib.SMTPRecipientsRefused as e:
        print(f"\n❌ RECIPIENT ERROR: {e}")
        print("   Gmail is refusing to send to this recipient")
        return False
        
    except smtplib.SMTPSenderRefused as e:
        print(f"\n❌ SENDER ERROR: {e}")
        print("   Gmail is refusing to send from this account")
        print("\nPossible causes:")
        print("  1. Account is temporarily locked due to suspicious activity")
        print("  2. Daily sending limit exceeded (500 emails/day)")
        print("  3. Account needs security verification")
        print("\nFix:")
        print("  1. Check: https://myaccount.google.com/security")
        print("  2. Verify account security status")
        print("  3. Wait 24 hours if daily limit exceeded")
        return False
        
    except smtplib.SMTPDataError as e:
        print(f"\n❌ DATA ERROR: {e}")
        error_code = str(e).split()[0] if str(e).split() else ""
        if "550" in error_code or "551" in error_code or "553" in error_code:
            print("   Gmail is blocking this email (likely spam/security)")
        print("\nPossible causes:")
        print("  1. Email content flagged as spam")
        print("  2. Too many emails sent recently")
        print("  3. Account security lock")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        print("\nPossible causes:")
        print("  1. Network connectivity issues")
        print("  2. Gmail server is down")
        print("  3. Firewall blocking SMTP")
        return False

if __name__ == "__main__":
    success = test_gmail_connection()
    sys.exit(0 if success else 1)

