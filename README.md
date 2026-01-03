# Agent Workflow

A 3-layer architecture for reliable AI-assisted workflows.

## Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the root directory. Minimum required variables:
   ```
   EMAIL_PASSWORD=your-gmail-app-specific-password
   COMPANY_NAME=Your Company Name
   SENDER_NAME=Your Name
   SMARTSUITE_API_KEY=your_smartsuite_api_key
   SMARTSUITE_WORKSPACE_ID=your_workspace_id
   ```
   
   Optional variables (defaults shown):
   - `SMTP_SERVER=smtp.gmail.com` (default)
   - `SMTP_PORT=587` (default)
   - `EMAIL_FROM=04isaacag@gmail.com` (default)
   - `CALENDAR_LINK=https://calendly.com/example/kickoff-call` (default example)
   - `COMPANY_BACKGROUND` (can be provided per-email instead)
   
   **To get SmartSuite credentials:**
   - API Key: SmartSuite → User Profile → API Settings → Generate New API Key
   - Workspace ID: First 8 characters in URL after `https://app.smartsuite.com/`

## Lead Generation Workflow (Apollo.io)

This workflow extracts B2B leads from Apollo.io and syncs them directly into your SmartSuite Leads table.

### Setup
1. Add your Apollo API Key to `.env`:
   ```
   APOLLO_API_KEY=your_apollo_api_key_here
   ```

### Usage
Run the lead generation script:
```bash
python3 execution/generate_leads_apollo.py
```

The script is configured to:
- Search for specific job titles (e.g., CTO, Founder)
- Filter for verified emails only
- Deduplicate leads against existing records in SmartSuite
- Sync lead details (Name, Company, Email, Title, LinkedIn)

For more details, see `directives/generate_leads_apollo.md`.

## Client Onboarding Workflow

To onboard a new client, simply say:
- "Onboard client email@example.com"
- "Onboard client email@example.com, name John Doe" (for personalization)

You can provide company background as bullet points when requesting onboarding. The system will:
1. Read the onboarding directive
2. Format your company background bullet points
3. Execute the email sending script with the provided information
4. Send a professional onboarding email from 04isaacag@gmail.com with company background and calendar link

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

## Architecture

- `directives/` - SOPs and workflow instructions
- `execution/` - Deterministic Python scripts
- `.tmp/` - Temporary files (not committed)
- `mcp_server_smartsuite.py` - MCP Server for SmartSuite integration

