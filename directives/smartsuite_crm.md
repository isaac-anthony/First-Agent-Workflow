# SmartSuite CRM Operations

## Goal
Enable full CRUD operations and automation within SmartSuite CRM via MCP Server integration. This allows the AI assistant to interact with your SmartSuite CRM data programmatically, enabling automation workflows and data management.

## Inputs
- API Token (stored in .env as `SMARTSUITE_API_KEY`)
- Workspace ID (stored in .env as `SMARTSUITE_WORKSPACE_ID`)
- Solution ID (for "Sales CRM Agent" solution or any other solution)
- Operation type and parameters

## Tools/Scripts
- `mcp_server_smartsuite.py` - MCP Server exposing SmartSuite tools
- `execution/smartsuite_client.py` - SmartSuite API client (deterministic wrapper)

## Available Operations

### 1. List Solutions
- **Tool**: `smartsuite_list_solutions`
- **Description**: Get all solutions in the workspace
- **Use Case**: Discover available solutions, find solution IDs

### 2. Get Solution Details
- **Tool**: `smartsuite_get_solution`
- **Description**: Get solution details including tables, fields, and structure
- **Use Case**: Understand solution schema before creating/updating records

### 3. List Records
- **Tool**: `smartsuite_list_records`
- **Description**: List records from a specific table
- **Parameters**: `solution_id`, `table_id`, optional `filters`
- **Use Case**: Retrieve all clients, view records in a table

### 4. Get Record
- **Tool**: `smartsuite_get_record`
- **Description**: Get a specific record by ID
- **Parameters**: `solution_id`, `table_id`, `record_id`
- **Use Case**: Retrieve details for a specific client or record

### 5. Create Record
- **Tool**: `smartsuite_create_record`
- **Description**: Create a new record in a table
- **Parameters**: `solution_id`, `table_id`, `data` (key-value pairs)
- **Use Case**: Add new clients, create opportunities, log activities

### 6. Update Record
- **Tool**: `smartsuite_update_record`
- **Description**: Update an existing record
- **Parameters**: `solution_id`, `table_id`, `record_id`, `data`
- **Use Case**: Update client status, modify record fields

### 7. Delete Record
- **Tool**: `smartsuite_delete_record`
- **Description**: Delete a record
- **Parameters**: `solution_id`, `table_id`, `record_id`
- **Use Case**: Remove records (use with caution)

### 8. Search Records
- **Tool**: `smartsuite_search_records`
- **Description**: Search records with a query string
- **Parameters**: `solution_id`, `table_id`, `query`
- **Use Case**: Find clients by name, search for specific records

## Process Flow

1. **MCP Server Setup**: The MCP server exposes SmartSuite operations as tools
2. **Tool Invocation**: AI assistant calls tools via MCP protocol
3. **API Execution**: Tools execute deterministic API calls via `SmartSuiteClient`
4. **Result Return**: Results returned as JSON for AI processing

## Configuration

Add to `.env`:
```
SMARTSUITE_API_KEY=your_api_token_here
SMARTSUITE_WORKSPACE_ID=your_workspace_id_here
```

**To get your credentials:**
1. **API Key**: Log in to SmartSuite → User Profile → API Settings → Generate New API Key
2. **Workspace ID**: First 8 characters in URL after `https://app.smartsuite.com/`

## Integration with Other Workflows

### Onboarding Workflow Integration
- After sending onboarding email, automatically create client record in SmartSuite
- Update client status to "Onboarded" after kickoff call
- Link email communications to client records

### Example Workflow
1. User: "Onboard client email@example.com"
2. System sends onboarding email
3. System creates client record in SmartSuite CRM
4. System updates record with onboarding date and status

### Data Retrieval
- Pull client information for personalized emails
- Retrieve client history before interactions
- Get client status for workflow routing

## Error Handling

- **Authentication Errors**: Check API key and workspace ID
- **Invalid IDs**: Verify solution_id and table_id exist
- **Missing Fields**: Ensure data object includes required fields
- **API Limits**: Handle rate limiting gracefully

## Best Practices

1. **Always get solution structure first** before creating/updating records
2. **Validate data** against table schema before API calls
3. **Handle errors gracefully** and provide clear error messages
4. **Use search** before creating to avoid duplicates
5. **Log operations** for audit trail

## Testing

Before using in production:
1. Test with a test solution/table
2. Verify all CRUD operations work
3. Test error handling with invalid inputs
4. Verify integration with other workflows




