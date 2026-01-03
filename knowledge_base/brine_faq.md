# Brine.ai Knowledge Base & SOPs

This document contains the core information that the AI Agent uses to answer lead questions and draft personalized replies.

## 1. Company Overview
Brine.ai builds "Agentic Workflows." We don't just provide chatbots; we build autonomous agents that can scrape data, sync with CRMs, send emails, and handle lead maintenance.

## 2. PRICING & TIER STRUCTURE
**Question**: What is included in the $1,000/month "Starter Template" versus the $5,000/month "Enterprise Agent"?
**Answer**: The Starter Tier ($1,000) includes one out-of-the-box outreach automation template, single-channel scraping (LinkedIn or Email), and basic knowledge base integration. The Enterprise Tier ($5,000) includes full multi-agent orchestrators, cross-platform workflows, unlimited data sources, 1-on-1 technical consulting, and deep-link API integrations into proprietary software.

## 3. SECURITY & DATA PRIVACY
**Question**: How do you train the agent on my business data and ensure it stays private?
**Answer**: We utilize Zero-Trust Data Architecture. Your data is stored in a siloed vectorized environment. We use RAG (Retrieval-Augmented Generation) to ensure the agent only retrieves your information for your specific tasks. Your data is never used to train public models or shared with other clients.

## 4. LEAD SCRAPING & VERIFICATION
**Question**: Where do the leads come from and how do you ensure they are qualified?
**Answer**: Our agents use Multi-Signal Verification. We scrape from LinkedIn, Apollo, and niche directories. The agent analyzes "Intent Signals" (hiring changes, recent posts, or keyword triggers) and verifies every email through a real-time validation API to keep bounce rates below 1%.

## 5. INTEGRATIONS & LEGACY SYSTEMS
**Question**: Can your agent work with my CRM (Hubspot, GoHighLevel, SmartSuite) or old legacy databases?
**Answer**: Yes. Because our framework is built in Python, we can connect to any platform with a REST API. For legacy systems without APIs, we deploy Custom Execution Scripts (RPA) that allow the agent to navigate web interfaces just like a human would.

## 6. HUMAN-IN-THE-LOOP (HITL) PROTOCOLS
**Question**: What happens if a lead asks a complex question that isn't in the documentation?
**Answer**: The agent is programmed with an 85% Confidence Trigger. If it cannot find a definitive answer in the knowledge base, it will draft a "Pending Review" response and flag it for your manual approval rather than sending it automatically.

## 7. ONBOARDING & DEPLOYMENT TIMELINE
**Question**: How long does it take to get my agent live?
**Answer**: Our Rapid Deployment process takes 7 to 10 business days.
- Days 1-3: Data Ingestion (Reading your SOPs/Files).
- Days 4-6: Workflow Mapping (CRM/API connections).
- Days 7-10: Sandbox Testing & Agent Logic Verification.

## 8. AUTOMATED ONBOARDING (ENTERPRISE ONLY)
**Question**: Can the agent handle the actual onboarding of new clients?
**Answer**: Yes. In the Enterprise Tier, the agent can automatically generate contracts (via DocuSign/PandaDoc), create shared Slack channels, and set up client-specific Google Drive folders the moment a lead agrees to move forward.

## 9. TONE & BRAND VOICE CLONING
**Question**: Will the emails sound like a bot?
**Answer**: No. We use Dynamic Tone Mapping. The agent analyzes your past sent emails and communication style to clone your brand voice. It is instructed to avoid "AI-isms" and maintain a 1-to-1 human conversational feel.

## 10. HANDLING REJECTIONS & OOO
**Question**: How does the agent handle "Not Interested" or "Out of Office" replies?
**Answer**: The agent uses Sentiment Analysis. "Out of Office" replies are automatically rescheduled for a 7-day follow-up. "Not Interested" replies are tagged in your CRM for exclusion. "Positive" replies are prioritized and pushed to the top of your inbox.

## 11. SCALABILITY & USAGE COSTS
**Question**: If I scale to 10,000 leads, does my monthly price increase?
**Answer**: The $1,000 starter plan includes a fixed volume of verified leads. If you scale beyond your tier's limit, we move you to a Hybrid Performance Model where you only pay for extra compute/token usage, ensuring your ROI remains predictable.

## 12. HALLUCINATION PREVENTION
**Question**: How do you stop the AI from making up fake prices or facts?
**Answer**: We implement Strict Grounding Rules. The agent is explicitly forbidden from estimating numbers or promising features not found in the knowledge_base/. If information is missing, the agent is instructed to book a call with a human representative.

## 13. REPORTING & ANALYTICS
**Question**: How do I track the agent's performance?
**Answer**: You receive a Weekly Revenue Attribution Report. This tracks leads scraped, open rates, sentiment breakdown, and the total dollar value of the meetings booked by the agent.

## 14. Demo & Booking
**Demo Video**: https://brine.ai/demo-video
**Booking Link**: https://calendly.com/brine-ai/demo

## 15. SOP: Handling Interest
When a lead is interested, always thank them for their interest, answer any specific technical questions they have using the information above, and then provide the booking link: https://calendly.com/brine-ai/demo.

