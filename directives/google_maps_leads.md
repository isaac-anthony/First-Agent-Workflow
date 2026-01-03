# Google Maps Small Business Lead Generation & Nurture Agent

## Goal
Extract **Qualified B2B leads**, perform initial outreach, and maintain the sales funnel through automated reply detection, sentiment analysis, and nurture cycles for Brine.ai.

## Qualification Criteria
1.  **Phone Number**: Mandatory. Must be present in Google Maps.
2.  **Email Address**: Mandatory. Must be successfully found on the business website.
3.  **Lead Name**: Mandatory. Fallback: "Team at [Business Name]".
4.  **Mandatory Rule**: If any of the above are missing, the lead is DISQUALIFIED.

## Process Phases

### Phase 1: Search & Sync
- Scrape Google Maps for businesses.
- Qualify leads (Phone + Email + Name).
- Sync qualified leads to Google Sheets with `Contacted? = No`.

### Phase 2: Initial Outreach
- Send the "Brine.ai Intro Email".
- Update sheet: `Contacted? = Yes`, `Time Contacted = [Timestamp]`, `Status = Pending`.

### Phase 3: Maintenance & Nurture (Janitor Mode)
The agent monitors the sheet and your Gmail inbox daily:
1.  **Sentiment Analysis**: The agent reads incoming replies from leads.
    - **"Not Interested"**: Agent sends the **Demo Video Email** and updates status to "Archived (Not Interested)".
    - **"Interested"**: Agent updates status to "Interested" and alerts you.
    - **"Neutral"**: Agent updates status to "Pending (Neutral Reply)" for your review.
2.  **Automated Follow-up**: If no reply is detected after 7 days, the agent sends a follow-up email and updates status to "Followed Up".

## Google Sheets Status Guide
- **Pending**: Initial email sent, waiting for reply.
- **Interested**: Lead wants to talk! (Automated follow-ups stop).
- **Not Interested**: Lead declined (Agent sends video then archives).
- **Followed Up**: One follow-up email has been sent.
- **Archived**: Final state, no further action.

## Tools/Scripts
- `execution/scrape_google_maps.py`: Scraper.
- `execution/extract_website_data.py`: Email finder.
- `execution/gmail_client.py`: Gmail reader (via API).
- `execution/sentiment_analyzer.py`: AI-powered reply classification (via ChatGPT).
- `execution/google_sheets_client.py`: Data manager.
- `execution/send_intro_email.py`: Intro outreach.
- `execution/send_nurture_email.py`: Follow-ups & Demo video emails.
- `execution/orchestrate_maps_workflow.py`: Discovery orchestrator.
- `execution/maintain_leads.py`: Nurture orchestrator (Janitor Mode).

## Security & Privacy
- **API Keys**: Stored only in `.env` (Excluded from GitHub via `.gitignore`).
- **OAuth Tokens**: Stored locally in `token.json` and `token_gmail.json` (Excluded from GitHub).
- **Credentials**: `credentials.json` and `credentials.actual.json` are strictly excluded from version control.
