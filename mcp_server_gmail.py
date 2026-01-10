#!/usr/bin/env python3
"""
MCP Server for Gmail Integration
Exposes Gmail operations as MCP tools for AI assistants
"""

import asyncio
import json
import os
import sys
import smtplib
import re
from typing import Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from dotenv import load_dotenv

# Add execution directory to path for imports if needed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'execution'))

load_dotenv()

try:
    from mcp.server import Server
    from mcp.server.models import Tool, TextContent
    from mcp.types import Tool as MCPTool
except ImportError:
    print("MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Import the onboarding logic if available
try:
    from send_onboarding_email import send_onboarding_email, validate_email
except ImportError:
    # Fallback validation if import fails
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    send_onboarding_email = None

# Create MCP server
server = Server("gmail-integration")

@server.list_tools()
async def list_tools() -> list[MCPTool]:
    """List all available Gmail tools."""
    tools = [
        Tool(
            name="gmail_send_email",
            description="Send a plain text email to a recipient",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body content"
                    }
                },
                "required": ["to", "subject", "body"]
            }
        )
    ]
    
    if send_onboarding_email:
        tools.append(
            Tool(
                name="gmail_send_onboarding_email",
                description="Send a professional onboarding email using the standard template",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "client_email": {
                            "type": "string",
                            "description": "Client's email address"
                        },
                        "client_name": {
                            "type": "string",
                            "description": "Optional client name for personalization"
                        }
                    },
                    "required": ["client_email"]
                }
            )
        )
    
    return tools

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

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "gmail_send_email":
            result = send_basic_email(
                arguments["to"],
                arguments["subject"],
                arguments["body"]
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "gmail_send_onboarding_email":
            if not send_onboarding_email:
                return [TextContent(type="text", text="Onboarding module not found")]
            
            result = send_onboarding_email(
                arguments["client_email"],
                arguments.get("client_name")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]

async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())



