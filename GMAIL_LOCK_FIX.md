# Gmail Lock/Blocking Fix

## Problem
Messages were being "locked" in Gmail - emails not sending or being blocked.

## Root Causes Identified

1. **Gmail Daily Limit**: Personal Gmail accounts have a **500 emails/day limit**
2. **Rate Limiting**: Sending too many emails too quickly triggers Gmail's spam filters
3. **Account Security Lock**: Gmail may temporarily lock accounts due to suspicious activity
4. **Poor Error Handling**: Errors weren't being properly diagnosed

## Fixes Applied

### 1. ✅ Enhanced Error Handling
**Files**: `execution/send_onboarding_email.py`, `execution/gmail_client.py`

- Added specific error handling for:
  - `SMTPAuthenticationError` - App password issues
  - `SMTPSenderRefused` - Account locked or daily limit exceeded
  - `SMTPDataError` - Email blocked (550, 551, 553 errors)
  - `SMTPRecipientsRefused` - Recipient issues

- Better error messages with actionable fixes

### 2. ✅ Gmail Rate Limiter
**File**: `execution/gmail_rate_limiter.py` (NEW)

- Tracks daily and hourly email counts
- Prevents sending when limits are reached
- Automatic reset at midnight (daily) and top of hour (hourly)
- Persists stats to `knowledge_base/gmail_sending_stats.json`

**Limits**:
- Daily: 500 emails/day (Gmail personal account limit)
- Hourly: 100 emails/hour (conservative limit)
- Minimum delay: 5 seconds between emails

### 3. ✅ Gmail Diagnostic Tool
**File**: `execution/diagnose_gmail.py` (NEW)

Run this to check Gmail status:
```bash
python3 execution/diagnose_gmail.py
```

Tests:
- SMTP connection
- Authentication
- Email sending capability

### 4. ✅ Better Logging
All email sending now includes:
- Clear error messages
- Actionable fix suggestions
- Rate limit status

## How to Check Gmail Status

### Option 1: Run Diagnostic Tool
```bash
python3 execution/diagnose_gmail.py
```

### Option 2: Check Rate Limits
```python
from execution.gmail_rate_limiter import GmailRateLimiter
limiter = GmailRateLimiter()
status = limiter.get_status()
print(status)
```

## Common Issues & Fixes

### Issue: "Gmail Sender Refused"
**Cause**: Daily limit exceeded or account locked

**Fix**:
1. Check: https://myaccount.google.com/security
2. Verify account security status
3. Wait 24 hours if daily limit exceeded
4. Complete any security challenges

### Issue: "Gmail Authentication Error"
**Cause**: App Password is incorrect or expired

**Fix**:
1. Go to: https://myaccount.google.com/apppasswords
2. Generate a new App Password
3. Update `EMAIL_PASSWORD` in `.env`

### Issue: "Gmail Data Error (550/551/553)"
**Cause**: Email blocked due to spam/security

**Fix**:
1. Check Gmail security: https://myaccount.google.com/security
2. Verify account isn't locked
3. Reduce sending frequency
4. Check email content for spam triggers

## Prevention

1. **Rate Limiting**: Already implemented (5 seconds between emails)
2. **Daily Tracking**: Rate limiter prevents exceeding 500/day
3. **Error Detection**: Better error handling catches issues early
4. **Status Monitoring**: Use diagnostic tool regularly

## Next Steps

If emails are still being locked:

1. **Run diagnostic**: `python3 execution/diagnose_gmail.py`
2. **Check Gmail security**: https://myaccount.google.com/security
3. **Verify App Password**: Make sure it's not expired
4. **Check daily limit**: Review `knowledge_base/gmail_sending_stats.json`
5. **Wait if needed**: If daily limit exceeded, wait 24 hours

## Files Modified

- `execution/send_onboarding_email.py` - Enhanced error handling + rate limiting
- `execution/gmail_client.py` - Enhanced error handling
- `execution/gmail_rate_limiter.py` - NEW: Rate limiting system
- `execution/diagnose_gmail.py` - NEW: Diagnostic tool

