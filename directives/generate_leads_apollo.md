# Apollo.io Lead Generation Workflow

## Goal
Automate the extraction of B2B leads from Apollo.io and sync them into the SmartSuite CRM Leads table to maintain a steady pipeline of prospects.

## Inputs
- `target_titles`: List of job titles to search for (e.g., ["CTO", "Founder"])
- `target_locations`: List of locations (e.g., ["United States", "London"])
- `limit`: Maximum number of leads to fetch per run (default: 5)

## Tools/Scripts
- `execution/generate_leads_apollo.py` - The core execution engine for fetching and syncing leads.
- `execution/smartsuite_client.py` - Deterministic client for SmartSuite API operations.

## Process
1. **API Initialization**: Load Apollo and SmartSuite credentials from `.env`.
2. **Lead Discovery**: Call Apollo's `mixed_people/search` API with the provided criteria.
3. **Verification**: Filter results to ensure only leads with confirmed email addresses are processed.
4. **Deduplication**: Query the SmartSuite Leads table to check if a record with the same email already exists.
5. **Data Mapping**: Transform Apollo's nested JSON response into the flat field structure required by SmartSuite.
6. **CRM Integration**: Create a new record in the "Leads" table for each unique, verified prospect.
7. **Reporting**: Provide a summary of found vs. synced leads.

## Outputs
- Success message for each lead synced.
- Summary report (e.g., "Found 5 leads, 3 synced, 2 skipped as duplicates").
- Error logs for any failed API requests.

## SmartSuite Configuration
- **Solution ID**: `69575be937f6f09c44f19154` (Sales CRM Agent)
- **Leads Table ID**: `6818e4145aa2a5a36b354d60`
- **Field Mappings**:
  - Full Name -> `s3e2e7e115` (Nested: `first_name`, `last_name`)
  - Email -> `sb8f7c7254` (Single Email field)
  - Company Name -> `sec468eef2` (New Account text area)
  - Job Title -> `priority` (Single Select: urgent, high, normal, low)
  - Notes/Source -> `description` (Rich Text)

## Data Extraction Requirements
To successfully populate the Leads table, the scraping workflow must extract:
1. **First & Last Name**: Required for the `s3e2e7e115` field.
2. **Email Address**: Critical for the `sb8f7c7254` field.
3. **Company Name**: To be placed in `sec468eef2`.
4. **Source Link**: To be stored in the `description` for traceability.

## Edge Cases
- **No Email Found**: Skip the lead; do not create a record without a contact method.
- **Duplicate Lead**: If email exists in SmartSuite, skip creation to avoid CRM clutter.
- **Rate Limiting**: Apollo API has strict limits; the script should handle 429 errors gracefully (or the orchestrator should back off).
- **Missing API Keys**: The script must fail early with a clear message if `.env` is incomplete.

## Testing
1. Run with a small limit (e.g., `limit=1`) to verify field mappings.
2. Check the "Leads" table in SmartSuite to ensure data appears in the correct columns.
3. Verify that running the same search twice does not create duplicate records.
