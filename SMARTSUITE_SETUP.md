# SmartSuite MCP Server Setup Guide

## Overview

This MCP Server provides a wrapper around your SmartSuite CRM, allowing AI assistants to perform full CRUD operations on your CRM data.

## Prerequisites

1. SmartSuite account with API access
2. Python 3.9 or higher
3. MCP-compatible AI assistant (Cursor, Claude Desktop, etc.)

## Step 1: Get Your SmartSuite Credentials

### API Key
1. Log in to your SmartSuite workspace
2. Click your profile icon in the top-right corner
3. Select "My Profile" or "API Settings"
4. Scroll to the "API Key" section
5. Click "Generate New API Key"
6. Copy and securely store the key (you won't see it again!)

### Workspace ID
1. While logged into SmartSuite, look at your browser's address bar
2. The URL will look like: `https://app.smartsuite.com/12345678/home`
3. The first 8 characters after `/app.smartsuite.com/` are your Workspace ID
4. In this example, `12345678` is the Workspace ID

## Step 2: Configure Environment Variables

Add these to your `.env` file:

```bash
SMARTSUITE_API_KEY=your_api_key_here
SMARTSUITE_WORKSPACE_ID=your_workspace_id_here
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note on MCP SDK:**
The MCP Python SDK package name may vary. Try:
- `pip install mcp`
- `pip install mcp-python-sdk`
- Or check the official MCP documentation for the correct package name

If the MCP SDK isn't available as a Python package, you may need to:
1. Use the TypeScript/JavaScript MCP SDK instead
2. Or implement a custom MCP protocol handler

## Step 4: Test the Connection

Before setting up the MCP server, test your credentials:

```bash
python3 execution/test_smartsuite.py
```

This will:
- Verify your API key and workspace ID
- Test the connection to SmartSuite
- List your available solutions

If successful, you'll see your solutions listed.

## Step 5: Configure MCP Server in Your AI Assistant

### For Cursor

1. Open Cursor settings
2. Navigate to MCP Servers configuration
3. Add a new server with:
   ```json
   {
     "name": "smartsuite-crm",
     "command": "python3",
     "args": ["/path/to/Agent Workflow/mcp_server_smartsuite.py"],
     "env": {
       "SMARTSUITE_API_KEY": "your_key",
       "SMARTSUITE_WORKSPACE_ID": "your_workspace_id"
     }
   }
   ```

### For Claude Desktop

1. Open Claude Desktop settings
2. Navigate to MCP Servers
3. Add configuration similar to Cursor above

## Step 6: Verify It Works

Once configured, test by asking your AI assistant:
- "List all solutions in SmartSuite"
- "What solutions do I have in SmartSuite?"

If the MCP server is working, the AI will be able to call SmartSuite tools.

## Available Operations

Once set up, you can use these operations:

1. **List Solutions** - See all your SmartSuite solutions
2. **Get Solution Details** - Get tables and structure of a solution
3. **List Records** - Get all records from a table
4. **Get Record** - Get a specific record
5. **Create Record** - Add new records
6. **Update Record** - Modify existing records
7. **Delete Record** - Remove records
8. **Search Records** - Search with queries

## Integration with Onboarding Workflow

You can now integrate SmartSuite with your onboarding workflow:

1. When onboarding a client, create a record in SmartSuite
2. Update client status after kickoff calls
3. Pull client data for personalized communications

Example workflow:
- User: "Onboard client email@example.com"
- System sends email AND creates SmartSuite record
- System updates record with onboarding date

## Troubleshooting

### "MCP SDK not installed"
- Install the MCP SDK package (see Step 3)
- Or use alternative MCP implementation

### "SMARTSUITE_API_KEY not found"
- Verify `.env` file exists and has the correct variable names
- Check that you're running from the correct directory

### "HTTP 401: Unauthorized"
- Verify your API key is correct
- Check that the API key hasn't been revoked
- Ensure you're using the full API key (not truncated)

### "HTTP 404: Not Found"
- Verify your Workspace ID is correct (8 characters)
- Check that the solution/table IDs exist

### MCP Server Not Connecting
- Verify the Python path in MCP configuration
- Check that all dependencies are installed
- Review MCP server logs for errors
- Ensure the script is executable: `chmod +x mcp_server_smartsuite.py`

## Security Notes

- **Never commit your `.env` file** - it's in `.gitignore` for a reason
- **Rotate API keys regularly** for security
- **Use minimum required permissions** for API keys
- **Store credentials securely** - treat API keys like passwords

## Next Steps

1. Test basic operations (list solutions, get records)
2. Integrate with onboarding workflow
3. Create custom automation workflows
4. Connect to other business processes

For detailed operation documentation, see `directives/smartsuite_crm.md`.




