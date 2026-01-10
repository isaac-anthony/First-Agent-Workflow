#!/usr/bin/env python3
"""
Simplified MCP Server for SmartSuite CRM Integration
Works with Python 3.9+ without requiring the official MCP SDK
Uses JSON-RPC over stdio (standard MCP protocol)
"""

import json
import os
import sys
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# Add execution directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'execution'))

load_dotenv()

from smartsuite_client import SmartSuiteClient

# Initialize SmartSuite client
api_key = os.getenv('SMARTSUITE_API_KEY')
workspace_id = os.getenv('SMARTSUITE_WORKSPACE_ID')

if not api_key or not workspace_id:
    print(json.dumps({
        "jsonrpc": "2.0",
        "id": None,
        "error": {
            "code": -32600,
            "message": "SMARTSUITE_API_KEY and SMARTSUITE_WORKSPACE_ID must be set in .env"
        }
    }), file=sys.stderr)
    sys.exit(1)

smartsuite_client = SmartSuiteClient(api_key, workspace_id)

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
                "name": "smartsuite-crm",
                "version": "1.0.0"
            }
        }
    }

def handle_tools_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle tools/list request."""
    tools = [
        {
            "name": "smartsuite_list_solutions",
            "description": "List all solutions in the SmartSuite workspace",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "smartsuite_get_solution",
            "description": "Get solution details including tables and structure",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "solution_id": {
                        "type": "string",
                        "description": "The ID of the solution to retrieve"
                    }
                },
                "required": ["solution_id"]
            }
        },
        {
            "name": "smartsuite_list_records",
            "description": "List records from a SmartSuite table/solution",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "solution_id": {"type": "string"},
                    "table_id": {"type": "string"},
                    "filters": {"type": "object", "description": "Optional filters"}
                },
                "required": ["solution_id", "table_id"]
            }
        },
        {
            "name": "smartsuite_get_record",
            "description": "Get a specific record by ID",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "solution_id": {"type": "string"},
                    "table_id": {"type": "string"},
                    "record_id": {"type": "string"}
                },
                "required": ["solution_id", "table_id", "record_id"]
            }
        },
        {
            "name": "smartsuite_create_record",
            "description": "Create a new record in SmartSuite",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "solution_id": {"type": "string"},
                    "table_id": {"type": "string"},
                    "data": {"type": "object", "description": "Record data"}
                },
                "required": ["solution_id", "table_id", "data"]
            }
        },
        {
            "name": "smartsuite_update_record",
            "description": "Update an existing record",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "solution_id": {"type": "string"},
                    "table_id": {"type": "string"},
                    "record_id": {"type": "string"},
                    "data": {"type": "object"}
                },
                "required": ["solution_id", "table_id", "record_id", "data"]
            }
        },
        {
            "name": "smartsuite_delete_record",
            "description": "Delete a record from SmartSuite",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "solution_id": {"type": "string"},
                    "table_id": {"type": "string"},
                    "record_id": {"type": "string"}
                },
                "required": ["solution_id", "table_id", "record_id"]
            }
        },
        {
            "name": "smartsuite_search_records",
            "description": "Search records with a query string",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "solution_id": {"type": "string"},
                    "table_id": {"type": "string"},
                    "query": {"type": "string"}
                },
                "required": ["solution_id", "table_id", "query"]
            }
        }
    ]
    
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
        if tool_name == "smartsuite_list_solutions":
            result = smartsuite_client.list_solutions()
            return {
                "jsonrpc": "2.0",
                "id": params.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
        
        elif tool_name == "smartsuite_get_solution":
            result = smartsuite_client.get_solution(arguments["solution_id"])
            return {
                "jsonrpc": "2.0",
                "id": params.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
        
        elif tool_name == "smartsuite_list_records":
            result = smartsuite_client.list_records(
                arguments["solution_id"],
                arguments["table_id"],
                arguments.get("filters")
            )
            return {
                "jsonrpc": "2.0",
                "id": params.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
        
        elif tool_name == "smartsuite_get_record":
            result = smartsuite_client.get_record(
                arguments["solution_id"],
                arguments["table_id"],
                arguments["record_id"]
            )
            return {
                "jsonrpc": "2.0",
                "id": params.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
        
        elif tool_name == "smartsuite_create_record":
            result = smartsuite_client.create_record(
                arguments["solution_id"],
                arguments["table_id"],
                arguments["data"]
            )
            return {
                "jsonrpc": "2.0",
                "id": params.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
        
        elif tool_name == "smartsuite_update_record":
            result = smartsuite_client.update_record(
                arguments["solution_id"],
                arguments["table_id"],
                arguments["record_id"],
                arguments["data"]
            )
            return {
                "jsonrpc": "2.0",
                "id": params.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
        
        elif tool_name == "smartsuite_delete_record":
            result = smartsuite_client.delete_record(
                arguments["solution_id"],
                arguments["table_id"],
                arguments["record_id"]
            )
            return {
                "jsonrpc": "2.0",
                "id": params.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
        
        elif tool_name == "smartsuite_search_records":
            result = smartsuite_client.search_records(
                arguments["solution_id"],
                arguments["table_id"],
                arguments["query"]
            )
            return {
                "jsonrpc": "2.0",
                "id": params.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": params.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                }
            }
    
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": params.get("id"),
            "error": {
                "code": -32000,
                "message": f"Error executing {tool_name}: {str(e)}"
            }
        }

def main():
    """Main MCP server loop - reads JSON-RPC from stdin, writes to stdout."""
    # Read from stdin line by line
    for line in sys.stdin:
        if not line.strip():
            continue
        
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "initialize":
                response = handle_initialize(params)
            elif method == "tools/list":
                response = handle_tools_list(params)
            elif method == "tools/call":
                response = handle_tools_call(params)
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }
            
            print(json.dumps(response))
            sys.stdout.flush()
        
        except json.JSONDecodeError as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {
                    "code": -32000,
                    "message": f"Internal error: {str(e)}"
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    main()




