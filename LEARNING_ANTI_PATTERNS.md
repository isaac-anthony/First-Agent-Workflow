# Learning: Anti-Patterns & Prevention Strategies

## Email Automation Anti-Patterns

### 🚨 CRITICAL: Duplicate Email Prevention

#### Problem Pattern
**Symptom**: Leads receiving multiple initial outreach emails, including malformed emails like "Hi Yes,"

#### Root Causes Identified

1. **Multiple Entry Points Without Coordination**
   - Multiple scripts (`orchestrate_maps_workflow.py`, `send_pending_emails.py`) can send emails
   - No centralized "email sent" flag check before sending
   - Race conditions when both scripts run simultaneously

2. **Premature Maintenance Processing**
   - `maintain_leads.py` running before campaigns complete
   - Processing our own sent emails as "replies" from leads
   - Column index mix-ups (reading "Yes" from "Contacted?" as `lead_name`)

3. **Insufficient State Verification**
   - Not checking "Contacted?" column before sending
   - Not verifying sender email before processing as reply
   - Assuming sheet state matches actual email state

#### Prevention Checklist (ALWAYS Apply)

**Before Sending ANY Email:**
- [ ] Check "Contacted?" column = "No" or empty
- [ ] Check "Status" column (skip if "Pending", "Interested", "Archived")
- [ ] Verify lead email exists and is valid
- [ ] Check for duplicate emails in recent history (last hour)
- [ ] Mark as "Contacted? = Yes" IMMEDIATELY after successful send
- [ ] Update "Time Contacted" timestamp

**Before Processing Replies:**
- [ ] Verify `from_email` is NOT our own email address
- [ ] Verify `skip_my_email=True` in `get_latest_message_details()`
- [ ] Check thread has at least 2 messages (outreach + reply)
- [ ] Verify latest message is from lead, not from us

**Workflow Coordination:**
- [ ] Only ONE script should send initial emails per lead
- [ ] Maintenance scripts should run SEPARATELY, not before campaigns
- [ ] Use atomic operations: Check → Send → Mark (all in one transaction)

#### Code Patterns to Avoid

❌ **BAD**: Sending without checking
```python
# DON'T DO THIS
email_result = send_brine_intro_email(email, lead_name, biz_name)
sheets.mark_as_contacted(row_num)  # Too late - might send twice
```

✅ **GOOD**: Check first, then send, then mark
```python
# DO THIS
if contacted == "yes":
    continue  # Skip already contacted

email_result = send_brine_intro_email(email, lead_name, biz_name)
if email_result['success']:
    sheets.mark_as_contacted(row_num)  # Mark immediately
```

❌ **BAD**: Processing without sender verification
```python
# DON'T DO THIS
details = gmail.get_latest_message_details(thread_id)
if details and details.get('body'):
    # Process as reply - but might be our own email!
```

✅ **GOOD**: Verify sender first
```python
# DO THIS
details = gmail.get_latest_message_details(thread_id, skip_my_email=True)
if details and details.get('from_email') != my_email:
    # Safe to process as reply
```

#### Column Index Safety

**Problem**: Reading wrong column (e.g., "Yes" from "Contacted?" as `lead_name`)

**Solution**:
- Always use column names, not indices: `headers.index("Lead Name")`
- Validate column exists before accessing
- Use descriptive variable names: `col_lead_name` not `col_3`
- Add bounds checking: `if len(row) > col_lead_name`

#### State Management Principles

1. **Single Source of Truth**: Google Sheet is the source of truth for "Contacted?" status
2. **Immediate Updates**: Update sheet immediately after email send (don't batch)
3. **Idempotency**: Running the same script twice should not send duplicate emails
4. **Defensive Checks**: Always verify state before taking action

#### Testing Checklist

Before deploying email automation:
- [ ] Test with 1 lead: Verify only 1 email sent
- [ ] Test duplicate run: Run script twice, verify no duplicates
- [ ] Test maintenance: Verify it doesn't process our own emails
- [ ] Check sheet: Verify "Contacted?" marked correctly
- [ ] Monitor Gmail: Verify no malformed emails ("Hi Yes," etc.)

---

## General Automation Anti-Patterns

### 1. Race Conditions
**Pattern**: Multiple processes accessing same resource without coordination
**Prevention**: Use locks, check state before action, single entry point

### 2. State Desynchronization
**Pattern**: Sheet says one thing, reality is another
**Prevention**: Update immediately, verify after update, use transactions

### 3. Premature Processing
**Pattern**: Processing data before it's ready
**Prevention**: Wait for completion signals, check prerequisites

### 4. Column Index Confusion
**Pattern**: Reading wrong column due to index mix-up
**Prevention**: Use named columns, validate indices, add bounds checks

### 5. Missing Validation
**Pattern**: Assuming data is correct without checking
**Prevention**: Validate all inputs, check state before action, handle edge cases

---

## Key Takeaways for Future Development

1. **Always check state before sending emails** - Never assume
2. **Update state immediately after action** - Don't batch or delay
3. **Verify sender before processing replies** - Prevent false positives
4. **Use column names, not indices** - Prevents mix-ups
5. **Test for idempotency** - Scripts should be safe to run multiple times
6. **Separate concerns** - Don't mix maintenance with campaign execution
7. **Add defensive checks** - Better to skip than to duplicate

---

## Critical Bugs Fixed (2026-01-08)

### Bug Pattern 1: Control Flow Errors with Unreachable Code

**Symptom**: Code after `continue` or `return` statements in conditional blocks becomes unreachable, causing critical functionality to never execute.

**Example**:
```python
# ❌ BAD: Code after continue is unreachable
if condition:
    print("Processing...")
elif other_condition:
    continue  # This makes everything below unreachable!
    process_data()  # NEVER EXECUTES
    analyze_results()  # NEVER EXECUTES
```

**Fix Pattern**:
```python
# ✅ GOOD: All processing inside the if block
if condition:
    print("Processing...")
    process_data()  # Executes when condition is true
    analyze_results()  # Executes when condition is true
elif other_condition:
    continue  # Skip only when other_condition is true
```

**Detection Rules**:
- Look for `continue` or `return` statements followed by code in the same block
- Check if critical processing logic comes after early exit statements
- Verify all conditional branches properly contain their logic

**Prevention**:
- Always put processing logic INSIDE the condition block, not after `continue`/`return`
- Use code linters to detect unreachable code
- Test all conditional branches to ensure code executes

### Bug Pattern 2: Column Index Mismatches in Spreadsheet Operations

**Symptom**: Code updates wrong columns because column letters don't match the actual sheet header structure.

**Root Cause**: Column indices are hardcoded (P, Q, R) but don't match the actual header order defined in `initialize_sheet()`.

**Example**:
```python
# ❌ BAD: Assumes Contacted? is column P
sheets.update_cell(f"P{i}", "Yes", tab_name)  # Wrong column!

# Header actually defines:
# Column Q (index 16) = "Contacted?"
# Column R (index 17) = "Time Contacted"
```

**Fix Pattern**:
```python
# ✅ GOOD: Use column names from headers, not hardcoded letters
headers = ["Date Added", "Status", ..., "Contacted?", "Time Contacted", ...]
col_contacted_idx = headers.index("Contacted?")
col_contacted_letter = chr(65 + col_contacted_idx)  # Convert to letter
sheets.update_cell(f"{col_contacted_letter}{i}", "Yes", tab_name)
```

**Detection Rules**:
- Compare hardcoded column letters (P, Q, R) with actual header structure
- Verify `initialize_sheet()` headers match all `update_cell()` calls
- Check for column letter mismatches across multiple files

**Prevention Checklist**:
- [ ] Never hardcode column letters - always derive from headers
- [ ] Create helper function: `get_column_letter(header_name)`
- [ ] Verify column mappings match between `initialize_sheet()` and all update operations
- [ ] Add unit tests that verify column indices match headers
- [ ] Use column name constants instead of letters

**Helper Function Pattern**:
```python
def get_column_letter(headers: List[str], column_name: str) -> str:
    """Get column letter from header name."""
    try:
        idx = headers.index(column_name)
        return chr(65 + idx) if idx < 26 else 'A' + chr(65 + (idx - 26))
    except ValueError:
        raise ValueError(f"Column '{column_name}' not found in headers")
```

### Bug Pattern 3: Inconsistent Column References Across Files

**Symptom**: Different files use different column letters for the same data, causing data corruption.

**Example**:
- `google_sheets_client.py` updates columns P and Q
- `send_pending_emails.py` updates columns P and Q
- `maintain_leads.py` updates columns Q and R
- But headers define columns Q and R

**Fix Pattern**:
- Create a single source of truth for column mappings
- Use shared constants or helper functions
- Verify all files use the same column references

**Detection Rules**:
- Search for all `update_cell()` calls with column letters
- Compare column letters used across all files
- Verify they match the header structure

---

*Last Updated: 2026-01-08 - Added critical bug patterns from control flow and column index issues*
*Status: Active learning document - update as new patterns emerge*

