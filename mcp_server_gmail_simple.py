#!/usr/bin/env python3
"""
Simplified MCP Server for Gmail Integration
Works with Python 3.9+ without requiring the official MCP SDK
Uses JSON-RPC over stdio (standard MCP protocol)
"""

import json
import os
import sys
import smtplib
import re
from typing import Any, Dict, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from dotenv import load_dotenv

# Add execution directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'execution'))

load_dotenv()

# Import onboarding logic if available
try:
    from send_onboarding_email import send_onboarding_email, validate_email
except ImportError:
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    send_onboarding_email = None

def send_basic_email(to: str, subject: str, body: str) -> dict:
    """Helper to send a basic email using SMTP."""
    if not validate_email(to):
        return {"success": False, "message": f"Invalid email format: {to}"}
    
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    email_from = os.getenv('EMAIL_FROM', 'brineaiconsulting@gmail.com')
    email_password = os.getenv('EMAIL_PASSWORD')
    sender_name = os.getenv('SENDER_NAME', 'Isaac')
    
    if not email_password:
        return {"success": False, "message": "EMAIL_PASSWORD not found in environment"}
    
    msg = MIMEMultipart()
    msg['From'] = formataddr((sender_name, email_from))
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_from, email_password)
        server.sendmail(email_from, to, msg.as_string())
        server.quit()
        return {"success": True, "message": f"Email sent to {to}"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

def handle_initialize(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle initialize request."""
    return {
        "jsonrpc": "2.0",
        "id": params.get("id"),
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "gmail-integration",
                "version": "1.0.0"
            }
        }
    }

def handle_tools_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle tools/list request."""
    tools = [
        {
            "name": "gmail_send_email",
            "description": "Send a plain text email to a recipient",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body content"}
                },
                "required": ["to", "subject", "body"]
            }
        }
    ]
    
    if send_onboarding_email:
        tools.append({
            "name": "gmail_send_onboarding_email",
            "description": "Send a professional onboarding email using the standard template",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "client_email": {"type": "string", "description": "Client's email address"},
                    "client_name": {"type": "string", "description": "Optional client name"}
                },
                "required": ["client_email"]
            }
        })
    
    return {
        "jsonrpc": "2.0",
        "id": params.get("id"),
        "result": {
            "tools": tools
        }
    }

def handle_tools_call(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle tools/call request."""
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    try:
        if tool_name == "gmail_send_email":
            result = send_basic_email(
                arguments["to"],
                arguments["subject"],
                arguments["body"]
            )
        elif tool_name == "gmail_send_onboarding_email":
            if not send_onboarding_email:
                result = {"success": False, "message": "Onboarding module not found"}
            else:
                result = send_onboarding_email(
                    arguments["client_email"],
                    arguments.get("client_name")
                )
        else:
            return {
                "jsonrpc": "2.0",
                "id": params.get("id"),
                "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
            }
            
        return {
            "jsonrpc": "2.0",
            "id": params.get("id"),
            "result": {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
            }
        }
    
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": params.get("id"),
            "error": {"code": -32000, "message": str(e)}
        }

def main():
    """Main MCP server loop."""
    for line in sys.stdin:
        if not line.strip(): continue
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "initialize": response = handle_initialize(params)
            elif method == "tools/list": response = handle_tools_list(params)
            elif method == "tools/call": response = handle_tools_call(params)
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -32601, "message": f"Unknown method: {method}"}
                }
            print(json.dumps(response))
            sys.stdout.flush()
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {"code": -32000, "message": str(e)}
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    main()



