#!/usr/bin/env python3
"""
MCP Server for SmartSuite CRM Integration
Exposes SmartSuite operations as MCP tools for AI assistants
"""

import asyncio
import json
import os
import sys
from typing import Any, Optional
from dotenv import load_dotenv

# Add execution directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'execution'))

load_dotenv()

try:
    from mcp.server import Server
    from mcp.server.models import Tool, TextContent
    from mcp.types import Tool as MCPTool
except ImportError:
    print("MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

from smartsuite_client import SmartSuiteClient

# Initialize SmartSuite client
api_key = os.getenv('SMARTSUITE_API_KEY')
workspace_id = os.getenv('SMARTSUITE_WORKSPACE_ID')

if not api_key or not workspace_id:
    print("Error: SMARTSUITE_API_KEY and SMARTSUITE_WORKSPACE_ID must be set in .env", file=sys.stderr)
    sys.exit(1)

smartsuite_client = SmartSuiteClient(api_key, workspace_id)

# Create MCP server
server = Server("smartsuite-crm")

@server.list_tools()
async def list_tools() -> list[MCPTool]:
    """List all available SmartSuite tools."""
    return [
        Tool(
            name="smartsuite_list_solutions",
            description="List all solutions in the SmartSuite workspace",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="smartsuite_get_solution",
            description="Get solution details including tables and structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "solution_id": {
                        "type": "string",
                        "description": "The ID of the solution to retrieve"
                    }
                },
                "required": ["solution_id"]
            }
        ),
        Tool(
            name="smartsuite_list_records",
            description="List records from a SmartSuite table/solution",
            inputSchema={
                "type": "object",
                "properties": {
                    "solution_id": {
                        "type": "string",
                        "description": "Solution ID"
                    },
                    "table_id": {
                        "type": "string",
                        "description": "Table ID within the solution"
                    },
                    "filters": {
                        "type": "object",
                        "description": "Optional filters to apply (JSON object)"
                    }
                },
                "required": ["solution_id", "table_id"]
            }
        ),
        Tool(
            name="smartsuite_get_record",
            description="Get a specific record by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "solution_id": {"type": "string"},
                    "table_id": {"type": "string"},
                    "record_id": {"type": "string"}
                },
                "required": ["solution_id", "table_id", "record_id"]
            }
        ),
        Tool(
            name="smartsuite_create_record",
            description="Create a new record in SmartSuite",
            inputSchema={
                "type": "object",
                "properties": {
                    "solution_id": {"type": "string"},
                    "table_id": {"type": "string"},
                    "data": {
                        "type": "object",
                        "description": "Record data as key-value pairs matching table fields"
                    }
                },
                "required": ["solution_id", "table_id", "data"]
            }
        ),
        Tool(
            name="smartsuite_update_record",
            description="Update an existing record",
            inputSchema={
                "type": "object",
                "properties": {
                    "solution_id": {"type": "string"},
                    "table_id": {"type": "string"},
                    "record_id": {"type": "string"},
                    "data": {
                        "type": "object",
                        "description": "Fields to update as key-value pairs"
                    }
                },
                "required": ["solution_id", "table_id", "record_id", "data"]
            }
        ),
        Tool(
            name="smartsuite_delete_record",
            description="Delete a record from SmartSuite",
            inputSchema={
                "type": "object",
                "properties": {
                    "solution_id": {"type": "string"},
                    "table_id": {"type": "string"},
                    "record_id": {"type": "string"}
                },
                "required": ["solution_id", "table_id", "record_id"]
            }
        ),
        Tool(
            name="smartsuite_search_records",
            description="Search records with a query string",
            inputSchema={
                "type": "object",
                "properties": {
                    "solution_id": {"type": "string"},
                    "table_id": {"type": "string"},
                    "query": {
                        "type": "string",
                        "description": "Search query string"
                    }
                },
                "required": ["solution_id", "table_id", "query"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "smartsuite_list_solutions":
            result = smartsuite_client.list_solutions()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "smartsuite_get_solution":
            result = smartsuite_client.get_solution(arguments["solution_id"])
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "smartsuite_list_records":
            result = smartsuite_client.list_records(
                arguments["solution_id"],
                arguments["table_id"],
                arguments.get("filters")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "smartsuite_get_record":
            result = smartsuite_client.get_record(
                arguments["solution_id"],
                arguments["table_id"],
                arguments["record_id"]
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "smartsuite_create_record":
            result = smartsuite_client.create_record(
                arguments["solution_id"],
                arguments["table_id"],
                arguments["data"]
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "smartsuite_update_record":
            result = smartsuite_client.update_record(
                arguments["solution_id"],
                arguments["table_id"],
                arguments["record_id"],
                arguments["data"]
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "smartsuite_delete_record":
            result = smartsuite_client.delete_record(
                arguments["solution_id"],
                arguments["table_id"],
                arguments["record_id"]
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "smartsuite_search_records":
            result = smartsuite_client.search_records(
                arguments["solution_id"],
                arguments["table_id"],
                arguments["query"]
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        error_msg = f"Error executing {name}: {str(e)}"
        return [TextContent(type="text", text=error_msg)]

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



