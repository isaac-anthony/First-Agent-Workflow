# Sales CRM Agent Solution - Master Reference

> **DEFAULT CONTEXT**: This solution is the primary focus for all SmartSuite operations. When the user asks about SmartSuite, assume they mean the Sales CRM Agent solution unless otherwise specified.

## Solution Overview

- **Solution Name**: Sales CRM Agent
- **Solution ID**: `69575be937f6f09c44f19154`
- **Solution Slug**: `sju1g2g6`
- **Description**: SmartSuite for Sales CRM: Visualize, Manage, and Close Deals with Confidence
- **Workspace ID**: `s4egu9k1`

## Core Tables

The Sales CRM Agent solution contains the following core tables:

### Primary Tables (Most Used)
- **Contacts** - Primary table ID: `6818e40d8c8a260711ad1620` (22 records, slug: `sda94r3f`)
- **Opportunities** - Primary table ID: `69575be937f6f09c44f19161` (19 records, slug: `swkvz6sp`)

### Additional Tables
- **Accounts** - Multiple instances:
  - `6818e40d8c8a260711ad160d` (slug: `ss1yx9hl`)
  - `69575be937f6f09c44f19174` (slug: `s41m8579`)
- **Leads** - Table ID: `6818e4145aa2a5a36b354d60` (slug: `sycmfxgp`)
- **Team Leaders** - Table ID: `6830dce939feb956d83ca695` (slug: `s2zvxvo0`)
- **Contacts** (Additional instances - may be views or related tables):
  - `68190fb29095f506e013f324` (slug: `smik517b`)
  - `69575be937f6f09c44f19187` (slug: `s2riv82e`)
  - `67b3be6c3ed8716816feb199` (slug: `sjq1fb49`)

**Note**: When user refers to "Contacts" or "Opportunities", use the primary table IDs listed above unless they specify otherwise.

### 1. Contacts Table

**Table Information:**
- **Table ID**: `6818e40d8c8a260711ad1620`
- **Application Slug**: `sda94r3f`
- **Total Records**: 22 (as of exploration)

**Key Fields with Labels:**
- **Name Field**: `title` (Label: "Name") - Contains contact name
- **Company/Department Field**: `due_date` (Label: appears to be custom) - Contains company or department
- **Title/Role Field**: `priority` (Label: "Title") - Contains job title or role
- **Email Field**: `s000da1c94` (Label: "Email") - Array of email addresses
- **Phone Field**: `s5e03d44a2` (Label: "Phone") - Array of phone objects with structure:
  ```json
  {
    "phone_country": "MX",
    "phone_number": "55 1234 5678",
    "phone_extension": "",
    "phone_type": 2,
    "sys_root": "525512345678",
    "sys_title": "+52 55 1234 5678"
  }
  ```
- **Description**: `description` (Label: "Notes") - Text field for notes
- **Location**: `s9030a120f` (Label: "Location") - Address field object
- **Social Media**: `s16da9ea14` (Label: "Social") - Social network field with options
- **Birthday**: `sb96622cae` (Label: "Birthday") - Date field
- **VIP Status**: `sa25a1651d` (Label: "Vip?") - Yes/No field
- **Photo**: `sa27d1bd1a` (Label: "Photo") - File field
- **Linked Records**:
  - `s6f8d8ed19` (Label: "Opportunities") - Linked to Opportunities table
  - `s56e1c0948` (Label: "Account") - Linked to Accounts table

**Field Structure:**
- Most fields use internal IDs (e.g., `s000da1c94`, `s5e03d44a2`)
- Standard fields: `title`, `description`, `due_date`, `priority`
- Arrays are used for multi-value fields (emails, phones, linked records)

**Record Creation Pattern:**
```json
{
  "title": "Contact Name",
  "due_date": "Company Name",
  "priority": "Job Title",
  "s5e03d44a2": [{
    "phone_country": "MX",
    "phone_number": "55 1234 5678",
    "phone_extension": "",
    "phone_type": 2,
    "sys_root": "525512345678",
    "sys_title": "+52 55 1234 5678"
  }],
  "s000da1c94": ["email@example.com"],
  "description": ""
}
```

### 2. Opportunities Table

**Table Information:**
- **Table ID**: `69575be937f6f09c44f19161`
- **Application Slug**: `swkvz6sp`
- **Total Records**: 19 (as of exploration)

**Key Fields with Labels:**
- **Name Field**: `title` (Label: "Opportunity") - Opportunity name
- **Status Field**: `status` (Label: "Stage") - Dropdown/status object with structure:
  ```json
  {
    "value": "ready_for_review",  // or "in_progress", "complete", "Closed - Won"
    "updated_on": "2026-01-02T06:29:57.204000Z"
  }
  ```
  **Status Values Available:**
  - `backlog` (Label: "New")
  - `in_progress`
  - `ready_for_review` (may appear as "Scoping" in UI)
  - `complete`
  - `970b4837-724f-433a-b078-59e25ff9e60b` (custom status)
  - `Closed - Won` (exact format for closed won - may be custom)
- **Priority Field**: `priority` (Label: "Sales Team") - Dropdown with options: "urgent", "high"
- **Description**: `description` (Label: "Notes & Description") - Long text field
- **Assigned To**: `assigned_to` (Label: "Owner") - Array of user IDs
- **Due Date**: `due_date` - Date object
- **Custom Fields**:
  - `s318ec5004` (Label: "Estimated Value") - Currency field
  - `sdtvn5wj` (Label: "Actual Contract Value") - Currency field
  - `s4e1f88b60` (Label: "Likelihood to Close") - Percent complete field
  - `sk0pg3cq` (Label: "Priority") - Dropdown with options: "urgent", "high", plus custom values
  - `sb45bd1d58` (Label: "Quarter of Close") - Formula field (e.g., "Q1/2026")
  - `sotavmjs` (Label: "Actual Close Date") - Date field
  - `s7ea226547` (Label: "Next Actions") - Checklist field
  - `s6d60998f4` (Label: "Files and Attachments") - File field
  - `s8i74otx` (Label: "Contacts") - Linked records to Contacts table
  - `s5b71c0905` (Label: "Sales Assets") - Linked records
  - `s6w24p14` (Label: "Account") - Linked records to Accounts
  - `sxu2fsxw` (Label: "Quarters") - Linked records
  - `szirc2iy` (Label: "Activities") - Linked records
  - `scc4e49806` (Label: "Team Owner") - Linked records
  - `s1f8162bc5` (Label: "Is Quarter Current?") - Lookup field
  - `sc897dc8ef` (Label: "Record ID") - Record ID field

**Status Update Pattern:**
```json
{
  "status": {
    "value": "Closed - Won"  // Exact format matters
  }
}
```

**Important Notes:**
- Status field uses nested object structure: `{"value": "...", "updated_on": "..."}`
- Status values are case-sensitive and format-sensitive
- "Closed - Won" (with space and hyphen) is the correct format
- The `status` field is the primary field for opportunity stage/status

## API Endpoints

**Base URL**: `https://app.smartsuite.com/api/v1`

**Common Endpoints:**
- List Solutions: `GET /solutions/`
- Get Solution: `GET /solutions/{solution_id}/`
- List Applications/Tables: `GET /applications/`
- List Records: `POST /applications/{table_id}/records/list/`
- Get Record: `GET /applications/{table_id}/records/{record_id}/`
- Create Record: `POST /applications/{table_id}/records/`
- Update Record: `PUT /applications/{table_id}/records/{record_id}/`
- Delete Record: `DELETE /applications/{table_id}/records/{record_id}/`

**Authentication:**
- Header: `Authorization: Token {API_KEY}`
- Header: `Account-Id: {WORKSPACE_ID}`

## Common Operations

### Create Contact
```python
record_data = {
    "title": "Contact Name",
    "due_date": "Company",
    "priority": "Title",
    "s5e03d44a2": [phone_object],
    "s000da1c94": ["email@example.com"]
}
POST /applications/6818e40d8c8a260711ad1620/records/
```

### Update Opportunity Status
```python
update_data = {
    "status": {
        "value": "Closed - Won"
    }
}
PUT /applications/69575be937f6f09c44f19161/records/{record_id}/
```

### List Records
```python
POST /applications/{table_id}/records/list/
Body: {} or {"limit": 100}
Response: {"items": [...], "total": N}
```

## Field Naming Conventions

- **Standard Fields**: Use readable names (`title`, `description`, `status`, `priority`, `due_date`)
- **Custom Fields**: Use internal IDs starting with `s` followed by alphanumeric (e.g., `s5e03d44a2`, `s000da1c94`)
- **System Fields**: `id`, `application_id`, `application_slug`, `autonumber`, `first_created`, `last_updated`, `ranking`, `deleted_date`

## Custom Field Access

**YES - Full access to custom fields!**

Custom field metadata is available via the `structure` field in the application endpoint:
- **Endpoint**: `GET /applications/{table_id}/`
- **Field Info Location**: `structure` array contains all field definitions
- **Field Metadata Includes**:
  - `slug` - Field ID (e.g., `s318ec5004`, `status`)
  - `label` - Human-readable field name (e.g., "Estimated Value", "Stage")
  - `field_type` - Field type (e.g., `currencyfield`, `statusfield`, `linkedrecordfield`)
  - `params` - Field parameters including:
    - `choices` - Available options for dropdown/status fields
    - `required` - Whether field is required
    - `default_value` - Default value if any

**Field Mappings Stored In:**
- `.tmp/opportunities_field_mapping.json` - All Opportunities fields with labels
- `.tmp/contacts_field_mapping.json` - All Contacts fields with labels
- `.tmp/sales_crm_field_mappings.json` - Combined mappings

**Usage**: When creating/updating records, you can reference fields by:
- Field slug/ID (e.g., `s318ec5004`)
- Or by label if you look up the mapping first

## Data Patterns

### Phone Numbers
- Stored as array of objects
- Each object contains: `phone_country`, `phone_number`, `phone_extension`, `phone_type`, `sys_root`, `sys_title`
- `phone_type`: 2 = Mobile, other values for other types

### Email Addresses
- Stored as array of strings
- Field: `s000da1c94` for Contacts

### Status/Dropdown Fields
- Stored as objects with `value` key
- May include `updated_on` timestamp
- Values are case and format sensitive

### Dates
- Stored as objects: `{"date": "YYYY-MM-DD", "include_time": false}`
- Or: `{"date": null, "include_time": false}` for empty dates

## View Filtering

**Important**: SmartSuite views may filter records. The API may return fewer records than visible in SmartSuite UI if:
- View has active filters
- Records are on different pages
- View has specific criteria

**Solution**: Use direct table access or clear filters to see all records.

## Default Context Rules

1. **All SmartSuite operations default to Sales CRM Agent solution** unless user specifies otherwise
2. **Solution ID**: `69575be937f6f09c44f19154` (always use this for Sales CRM Agent)
3. **Primary Contacts table ID**: `6818e40d8c8a260711ad1620` (22 records)
4. **Primary Opportunities table ID**: `69575be937f6f09c44f19161` (19 records)
5. When user says "update a record", "create a contact", "list opportunities", etc., assume Sales CRM Agent context
6. Status updates for opportunities use format: `{"status": {"value": "Closed - Won"}}` (exact format with space and hyphen)
7. Always reference `directives/sales_crm_agent.md` for field structures and table IDs before operations

## Known Issues & Solutions

1. **Status field not updating**: Ensure exact format match (e.g., "Closed - Won" with space and hyphen)
2. **Records not appearing in API**: Check for view filters in SmartSuite UI
3. **Field IDs are internal**: Use field mapping above or explore record structure first
4. **Phone/Email arrays**: Must be arrays even for single values

## Integration Points

- **Onboarding Workflow**: Can create Contacts records after sending onboarding emails
- **Opportunity Management**: Can update opportunity statuses, create new opportunities
- **Data Retrieval**: Can pull contact/opportunity data for personalized communications

---

**Last Updated**: 2026-01-02
**Explored By**: AI Agent
**Status**: Active Reference Document

