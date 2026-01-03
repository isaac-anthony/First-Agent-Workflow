# MCP Server Setup for Cursor IDE

## Step 1: Use the Simplified MCP Server (No Installation Needed!)

**Good news!** We've created a simplified MCP server that works with Python 3.9+ and doesn't require installing the MCP SDK.

**Use this file instead:** `mcp_server_smartsuite_simple.py`

This version:
- ✅ Works with Python 3.9 (your current version)
- ✅ No additional packages needed (just uses standard library + requests)
- ✅ Implements the MCP protocol directly
- ✅ Same functionality as the SDK version

**Skip to Step 2** - you don't need to install anything!

## Step 2: Find Your Cursor Configuration File

Cursor stores MCP server configurations in a settings file. The location depends on your OS:

### macOS:
```
~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
```

### Windows:
```
%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
```

### Linux:
```
~/.config/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
```

**Alternative location (if above doesn't exist):**
Check Cursor's settings:
1. Open Cursor
2. Go to Settings (Cmd/Ctrl + ,)
3. Search for "MCP" or "Model Context Protocol"
4. Look for MCP server configuration section

## Step 3: Configure the MCP Server in Cursor

Add this configuration to your Cursor MCP settings file:

```json
{
  "mcpServers": {
    "smartsuite-crm": {
      "command": "python3",
      "args": [
        "/Users/isaacgutierrez/Cursor/Agent Workflow/mcp_server_smartsuite_simple.py"
      ],
      "env": {
        "SMARTSUITE_API_KEY": "079bf0f7e6cadcb06d41a8ee9c5296b3d3756c55",
        "SMARTSUITE_WORKSPACE_ID": "s4egu9k1"
      }
    }
  }
}
```

**Important Notes:**
- Replace the file path with the **full absolute path** to `mcp_server_smartsuite_simple.py`
- The path shown above is for your current setup: `/Users/isaacgutierrez/Cursor/Agent Workflow/mcp_server_smartsuite_simple.py`
- You can also reference environment variables from your `.env` file instead of hardcoding credentials

## Step 4: Alternative Configuration (Using .env file)

If you prefer to use your `.env` file (more secure), you can configure it like this:

```json
{
  "mcpServers": {
    "smartsuite-crm": {
      "command": "python3",
      "args": [
        "/Users/isaacgutierrez/Cursor/Agent Workflow/mcp_server_smartsuite_simple.py"
      ],
      "cwd": "/Users/isaacgutierrez/Cursor/Agent Workflow"
    }
  }
}
```

This way, the script will automatically load from `.env` (which it already does).

## Step 5: Restart Cursor

After adding the configuration:
1. Save the settings file
2. **Restart Cursor completely** (quit and reopen)
3. The MCP server should now be available

## Step 6: Verify It's Working

Once Cursor restarts, you can test by asking:
- "List all solutions in SmartSuite"
- "What solutions do I have?"

If the MCP server is working, I'll be able to call SmartSuite tools and interact with your CRM.

## Troubleshooting

### "MCP SDK not installed"
- Make sure you've installed the MCP Python SDK (Step 1)
- Try: `python3 -m pip install mcp`

### "Cannot find mcp_server_smartsuite_simple.py"
- Verify the file path is correct
- Use absolute path (starting with `/` on Mac/Linux or `C:\` on Windows)
- Make sure the file exists at that location

### "Module not found" errors
- Make sure you're using the same Python that has the packages installed
- Try using full path to Python: `/usr/bin/python3` or wherever your Python is

### MCP Server not appearing in Cursor
- Check Cursor's console/logs for errors
- Verify the JSON syntax is correct (no trailing commas)
- Make sure you restarted Cursor after adding the config

## Quick Test (Before Cursor Setup)

You can test the MCP server directly from terminal:

```bash
cd "/Users/isaacgutierrez/Cursor/Agent Workflow"
python3 mcp_server_smartsuite_simple.py
```

If it runs without errors, the server is working. Press Ctrl+C to stop it.

## Need Help?

If you're having trouble:
1. Check that `python3 execution/test_smartsuite.py` works (we already tested this ✓)
2. Verify the MCP SDK is installed: `python3 -c "import mcp; print('MCP installed')"`
3. Check Cursor's documentation for MCP server setup
4. Look at Cursor's console/logs for error messages

