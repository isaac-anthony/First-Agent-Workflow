# Agent Workflow: Brine.ai Agentic Sales Engine

A multi-layered, autonomous outbound lead generation and intake system designed to scale small business outreach using AI.

## Core Capabilities
*   **Automated Lead Discovery**: Scrapes Google Maps for local businesses based on niche and location.
*   **Website Intelligence**: Extracts contact data and context from business websites to verify lead quality.
*   **AI Lead Scoring**: Uses GPT-4o to rate leads (1-10) based on "The Breaking Point"—identifying high-volume businesses that need automation most.
*   **Personalized Outreach**: Generates unique, context-aware "hooks" for every lead to increase response rates.
*   **Intake & Sentiment Analysis**: Monitors Gmail for replies, classifies sentiment (Interested, OOO, Not Interested), and handles responses accordingly.
*   **Autonomous Nurturing**: Executes multi-stage follow-up sequences (3-7-14 day nudges) to ensure no lead is forgotten.
*   **Real-time Notifications**: Sends "Hot Lead" and "Interest Detected" alerts directly to Slack.
*   **Recursive Learning**: Automatically updates the `knowledge_base/` based on common questions and objections found in email threads.
*   **Executive Reporting**: Generates weekly performance summaries (leads found, contacted, interested, and weighted pipeline value) delivered via email and Google Sheets.

## Architecture
The system follows a 3-layer deterministic architecture:
1.  **Directives (`directives/`)**: High-level SOPs and AI instructions for the workflow.
2.  **Orchestration (`execution/`)**: Python-based engines that coordinate scraping, mailing, and maintenance.
3.  **Clients (`execution/`)**: Low-level integrations for Gmail, Google Sheets, Slack, and SmartSuite.

## Setup & Configuration
1.  **Install Dependencies**:
    pip install -r requirements.txt
    playwright install chromium
    2.  **Environment Variables**: Create a `.env` file with the following (placeholders shown):
    
    # Core Credentials
    OPENAI_API_KEY=your_openai_key
    SMARTSUITE_API_KEY=your_smartsuite_key
    SMARTSUITE_WORKSPACE_ID=your_workspace_id
    GOOGLE_SHEETS_ID=your_spreadsheet_id
    
    # Email Settings (Gmail App Password Required)
    EMAIL_FROM=your_email@gmail.com
    EMAIL_PASSWORD=your_app_password
    SMTP_SERVER=smtp.gmail.com
    SMTP_PORT=587
    
    # Notifications & Links
    SLACK_WEBHOOK_URL=your_slack_webhook
    CALENDAR_LINK=https://calendly.com/your-link
    COMPANY_NAME=Brine.ai
    SENDER_NAME=Isaac Gutierrez
    ## Usage

### 1. Run a Discovery & Outreach Campaign
Find new leads, score them, and send initial personalized emails:
python3 execution/orchestrate_maps_workflow.py config/targets.json### 2. Maintenance & Janitor Mode
Process replies, handle follow-ups, and update the CRM:
python3 execution/maintain_leads.py "Niche_Tab_Name"### 3. Weekly Executive Report
Aggregate stats from all campaigns and send a performance summary:
python3 execution/reporting_agent.py## SmartSuite CRM Integration
This project includes a dedicated MCP Server for SmartSuite, allowing an AI assistant to manage your CRM data directly.
*   **List/Search Records**: Find leads by status or niche.
*   **Sync Data**: Push qualified leads from Google Sheets to SmartSuite tables.
*   **Update Status**: Change lead status as they progress through the funnel.
python3 mcp_server_smartsuite.py

