# Gmail MCP Setup Guide

This guide will help you set up the Gmail MCP server in Cursor so you can send emails from your address (`brineaiconsulting@gmail.com`) using AI.

## Step 1: Generate a Gmail App Password

To allow the script to send emails through your Gmail account securely, you need an **App Password**.

1.  Go to your [Google Account settings](https://myaccount.google.com/).
2.  Navigate to **Security**.
3.  Under "How you sign in to Google," ensure **2-Step Verification** is turned on.
4.  Search for **App passwords** in the search bar at the top or find it under 2-Step Verification.
5.  Enter a name (e.g., "Cursor MCP") and click **Create**.
6.  **Copy the 16-character password** shown in the yellow box.

## Step 2: Credentials check

Your `.env` file is already updated with your Gmail address and App Password. You don't need to do anything here!

Current settings in `.env`:
*   `EMAIL_FROM=brineaiconsulting@gmail.com`
*   `EMAIL_PASSWORD=****` (App Password configured)
*   `SENDER_NAME=Isaac Gutierrez`

## Step 3: Configure MCP in Cursor

1.  Open **Cursor Settings** (Cmd + , on Mac).
2.  Go to **Features** -> **MCP**.
3.  Click **+ Add New MCP Server**.
4.  Fill in the details:
    *   **Name**: `gmail-integration`
    *   **Type**: `command`
    *   **Command**: `python3 "/Users/isaacgutierrez/Cursor/Agent Workflow/mcp_server_gmail_simple.py"`

Alternatively, if you prefer editing the settings file directly (as described in `MCP_SETUP_CURSOR.md`):

```json
{
  "mcpServers": {
    "gmail-integration": {
      "command": "python3",
      "args": [
        "/Users/isaacgutierrez/Cursor/Agent Workflow/mcp_server_gmail_simple.py"
      ],
      "cwd": "/Users/isaacgutierrez/Cursor/Agent Workflow"
    }
  }
}
```

## Step 4: Verify & Use

1.  Restart Cursor.
2.  Ask the AI: "Send a test email to [your-other-email]@example.com saying 'Hello from Cursor!'"
3.  The AI should call the `gmail_send_email` tool.

### Available Tools:
*   `gmail_send_email`: Send any plain text email.
*   `gmail_send_onboarding_email`: Sends a pre-formatted professional onboarding email (uses your existing template in `send_onboarding_email.py`).

