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

## Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. Create a `.env` file in the root directory. Minimum required variables:
   ```
   EMAIL_PASSWORD=your-gmail-app-specific-password
   COMPANY_NAME=Your Company Name
   SENDER_NAME=Your Name
   SMARTSUITE_API_KEY=your_smartsuite_api_key
   SMARTSUITE_WORKSPACE_ID=your_workspace_id
   OPENAI_API_KEY=your_openai_key
   GOOGLE_SHEETS_ID=your_spreadsheet_id
   SLACK_WEBHOOK_URL=your_slack_webhook
   CALENDAR_LINK=https://calendly.com/your-link
   ```
   
   Optional variables (defaults shown):
   - `SMTP_SERVER=smtp.gmail.com` (default)
   - `SMTP_PORT=587` (default)
   - `EMAIL_FROM=brineaiconsulting@gmail.com` (default)
   - `COMPANY_BACKGROUND` (can be provided per-email instead)
   
   **To get SmartSuite credentials:**
   - API Key: SmartSuite → User Profile → API Settings → Generate New API Key
   - Workspace ID: First 8 characters in URL after `https://app.smartsuite.com/`

## Architecture
The system follows a 3-layer deterministic architecture:
1.  **Directives (`directives/`)**: High-level SOPs and AI instructions for the workflow.
2.  **Orchestration (`execution/`)**: Python-based engines that coordinate scraping, mailing, and maintenance.
3.  **Clients (`execution/`)**: Low-level integrations for Gmail, Google Sheets, Slack, and SmartSuite.

## Usage

### 1. Run a Discovery & Outreach Campaign
Find new leads, score them, and send initial personalized emails:
```bash
python3 execution/orchestrate_maps_workflow.py config/targets.json
```

### 2. Maintenance & Janitor Mode
Process replies, handle follow-ups, and update the CRM:
```bash
python3 execution/maintain_leads.py "Niche_Tab_Name"
```

### 3. Weekly Executive Report
Aggregate stats from all campaigns and send a performance summary:
```bash
python3 execution/reporting_agent.py
```

### 4. Process CSV Leads
Process leads from a CSV file (e.g., Apollo.io export):
```bash
python3 execution/process_csv_leads.py path/to/leads.csv
```

## Client Onboarding Workflow

To onboard a new client, simply say:
- "Onboard client email@example.com"
- "Onboard client email@example.com, name John Doe" (for personalization)

You can provide company background as bullet points when requesting onboarding. The system will:
1. Read the onboarding directive
2. Format your company background bullet points
3. Execute the email sending script with the provided information
4. Send a professional onboarding email from brineaiconsulting@gmail.com with company background and calendar link

**Example company background format:**
- An Agentic Workflow consulting company
- Adds Agents into your business to increase business efficiency

## SmartSuite CRM Integration

The workspace includes an MCP Server for SmartSuite CRM that allows full CRUD operations:

- **List Solutions** - Get all solutions in workspace
- **Get Solution** - Get solution details and tables
- **List/Get/Create/Update/Delete Records** - Full record management
- **Search Records** - Search with query strings

**Setup:**
1. Add your SmartSuite API key and Workspace ID to `.env`
2. Install MCP SDK: `pip install mcp` (or follow MCP SDK installation guide)
3. Start MCP server: `python3 mcp_server_smartsuite.py`
4. Configure MCP server in your AI assistant (Cursor/Claude Desktop)

**Usage:**
Once configured, you can ask:
- "List all solutions in SmartSuite"
- "Create a new client record in the Sales CRM Agent solution"
- "Find all clients with status 'Active'"
- "Update client XYZ's status to 'Onboarded'"

See `directives/smartsuite_crm.md` for full documentation.
