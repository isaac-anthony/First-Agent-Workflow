# Self-Healing System & Autonomous Learning Loop

## Overview

The self-healing system implements autonomous learning and automatic issue prevention/detection for the email automation workflow. It learns from anti-patterns and automatically prevents duplicate emails, column mix-ups, and other common issues.

## Components

### 1. Self-Healing Agent (`execution/self_healing_agent.py`)

**Purpose**: Monitors, validates, and automatically fixes issues before they cause problems.

**Key Features**:
- ✅ Pre-send validation (prevents duplicate emails)
- ✅ Pre-reply validation (prevents false positives)
- ✅ Automatic sheet state auditing
- ✅ Auto-fixing common issues (column mix-ups, missing timestamps)
- ✅ Learning log for pattern detection
- ✅ Health reporting

**Main Methods**:
- `validate_before_send()` - Validates all conditions before sending email
- `validate_before_reply()` - Validates before processing replies
- `audit_sheet_state()` - Audits and auto-fixes sheet issues
- `learn_pattern()` - Learns new patterns for future detection

### 2. Learning Document (`LEARNING_ANTI_PATTERNS.md`)

**Purpose**: Documents all known anti-patterns and prevention strategies.

**Contents**:
- Root causes of issues
- Prevention checklists
- Code patterns to avoid vs. follow
- Testing strategies
- General automation anti-patterns

### 3. Integration Points

The self-healing agent is integrated into:

1. **`send_pending_emails.py`**
   - Validates before sending each email
   - Prevents duplicates and column mix-ups

2. **`orchestrate_maps_workflow.py`**
   - Validates before sending campaign emails
   - Prevents race conditions

3. **`maintain_leads.py`**
   - Validates before processing replies
   - Prevents false positives from our own emails

## How It Works

### Pre-Send Validation

Before sending ANY email, the agent checks:
1. ✅ "Contacted?" column = "No" or empty
2. ✅ "Status" column (skips if already processed)
3. ✅ Email is valid
4. ✅ No recent duplicate sends (last hour)
5. ✅ Lead_name is valid (not "Yes", "No", etc.)
6. ✅ No column index confusion

### Pre-Reply Validation

Before processing ANY reply, the agent checks:
1. ✅ `from_email` is NOT our own email
2. ✅ Thread has at least 2 messages
3. ✅ Latest message is from lead, not from us

### Automatic Auditing

The agent can audit the entire sheet and:
- Detect invalid lead_names (like "Yes" from column mix-up)
- Fix missing timestamps
- Detect status mismatches
- Generate health reports

### Learning Loop

1. **Detection**: Agent detects issues during validation
2. **Prevention**: Blocks problematic actions
3. **Logging**: Logs issues to learning log
4. **Learning**: Identifies patterns over time
5. **Auto-Fix**: Automatically fixes common issues during audits

## Usage

### Manual Audit

Run a full system audit:
```bash
python3 execution/self_healing_agent.py
```

Or use the audit script:
```bash
python3 execution/run_self_healing_audit.py
```

### Automatic Integration

The agent is automatically used in:
- Email sending workflows
- Reply processing workflows
- Campaign execution

### Scheduled Audits

Set up a cron job to run audits daily:
```bash
# Add to crontab (runs daily at 2 AM)
0 2 * * * cd /path/to/Agent\ Workflow && python3 execution/run_self_healing_audit.py
```

## Example Output

```
======================================================================
SELF-HEALING AGENT: AUDIT
======================================================================

Audited 57 leads. Found 57 issues, applied 57 fixes.

Statistics:
  total_leads: 57
  contacted: 0
  not_contacted: 57
  status_pending: 57
  potential_issues: 57

⚠️  Issues Found (57):
  - Row 2: Invalid lead_name 'Yes' (likely column mix-up)
  - Row 3: Invalid lead_name 'Yes' (likely column mix-up)
  ...

✅ Fixes Applied (57):
  - Row 2: Fixed invalid lead_name
  - Row 3: Fixed invalid lead_name
  ...
```

## Benefits

1. **Prevents Duplicate Emails**: Validates before every send
2. **Auto-Fixes Issues**: Fixes column mix-ups, missing data automatically
3. **Learns Patterns**: Identifies recurring issues
4. **Health Monitoring**: Tracks system health over time
5. **Zero Manual Intervention**: Fully autonomous

## Learning Log

The agent maintains a learning log at:
`knowledge_base/self_healing_log.json`

Contains:
- Issues detected
- Issues prevented
- Patterns learned
- Audit history

## Future Enhancements

- [ ] Machine learning for pattern detection
- [ ] Predictive issue prevention
- [ ] Automated testing integration
- [ ] Slack notifications for critical issues
- [ ] Performance metrics tracking

---

*Last Updated: After self-healing system implementation*
*Status: Active and learning*

