# Client Onboarding Workflow

## Goal
Send a professional onboarding email to a new client that introduces them to the company, provides background information, and invites them to a kickoff call via a calendar link.

## Inputs
- Client email address (required)
- Optional: Client name (for personalization)

Note: Company background bullet points are no longer used - the email template has a fixed, professional value proposition that is always the same.

## Tools/Scripts
- `execution/send_onboarding_email.py` - Sends the onboarding email

## Process
1. Validate the email address format
2. Read company information from environment variables (with defaults)
3. Personalize the email with client name (if provided) or use "Hi,"
4. Use the fixed email template with professional value proposition
5. Include calendar link for kickoff call (defaults to example link if not configured)
6. Send email via Gmail SMTP (defaults to brineaiconsulting@gmail.com)
7. Confirm delivery status

## Outputs
- Success confirmation with message ID (if available)
- Error message if sending fails

## Email Configuration
The following environment variables can be set in `.env` (defaults shown):
- `SMTP_SERVER` - SMTP server address (default: smtp.gmail.com)
- `SMTP_PORT` - SMTP port (default: 587)
- `EMAIL_FROM` - Sender email address (default: brineaiconsulting@gmail.com)
- `EMAIL_PASSWORD` - Email password or app-specific password (required)
- `COMPANY_NAME` - Your company name (required)
- `COMPANY_BACKGROUND` - Company background (optional, can be provided per-email)
- `CALENDAR_LINK` - URL to schedule the kickoff call (default: example link)
- `SENDER_NAME` - Name to appear in "From" field (required)

## Email Template Structure
The email always follows this exact format:

**Subject:** "Welcome to [Company Name] – Let's get started!"

**Body:**
1. Greeting: "Hi [Client Name]," (or "Hi," if no name provided)
2. Thank you message: "Thank you for choosing [Company Name]! We are thrilled to have you on board and are looking forward to working with you."
3. Value proposition: "We are excited to begin incorporating our AI agents into your workflow to help your business run as efficiently as possible. Our goal is to ensure your operations are streamlined, scalable, and powered by the best agentic technology available."
4. Next Steps: "Next Steps: We'd love to schedule a kickoff call to discuss your specific needs and map out how we can best serve you. Please use the link below to book a time that works for your schedule:"
5. Calendar link: "Book Your Kickoff Call Here [link]"
6. Closing: "We're looking forward to building something great together!"
7. Signature: "[Sender Name]\nFounder, [Company Name]"

**Important:** This template is fixed and always produces the same professional, high-energy, technically polished output. The company background bullet points are no longer used in the email body - the value proposition text is always the same.

## Edge Cases
- Invalid email format → Return error, don't attempt to send
- Missing environment variables → Return clear error listing what's missing
- SMTP connection failure → Return error with connection details
- Email sending failure → Return error with reason
- Empty calendar link → Still send email but note that calendar link is missing

## Error Handling
- Validate all inputs before attempting to send
- Provide clear error messages for debugging
- Log errors to console for troubleshooting

## Testing
Before using in production:
1. Test with your own email address
2. Verify email formatting and links
3. Confirm calendar link works
4. Check spam folder if email doesn't arrive

