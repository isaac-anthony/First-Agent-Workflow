#!/usr/bin/env python3
"""
Layer 3: Execution Script
AI Drafting Agent
Reads the knowledge base and drafts personalized, context-aware replies to leads.
"""

import os
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class DraftingAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.kb_path = os.path.join(os.path.dirname(__file__), "..", "knowledge_base", "brine_faq.md")

    def _get_knowledge_base(self) -> str:
        """Reads the knowledge base file."""
        try:
            with open(self.kb_path, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Warning: Could not read knowledge base at {self.kb_path}: {e}")
            return "No knowledge base available."

    def draft_reply(self, lead_text: str, lead_name: str) -> str:
        """
        Drafts a personalized reply to a lead's email using the knowledge base and objection battlesheets.
        """
        if not self.client:
            return f"Hi {lead_name},\n\nThank you for your interest! I'd love to chat. Book a call here: https://calendly.com/brine-ai/demo"

        kb_content = self._get_knowledge_base()
        
        prompt = f"""
        You are Isaac Gutierrez, Founder of Brine.ai. You are replying to a lead who has just emailed you.
        
        ### YOUR KNOWLEDGE BASE & OBJECTION BATTLESHEETS:
        {kb_content}
        
        ### LEAD'S EMAIL:
        \"{lead_text}\"
        
        ### INSTRUCTIONS:
        1. Address the lead by their name: {lead_name}.
        2. **DETECT OBJECTIONS**: If the lead mentions price, current tools, trust issues with AI, or being too small/big, use the specific "OBJECTION HANDLING BATTLESHEETS" in the knowledge base to draft a confident, helpful rebuttal.
        3. **ANSWER QUESTIONS**: If the lead asked a technical question, use the FAQ section to answer it accurately.
        4. **BE DECISIVE**: Don't just apologize. Explain WHY Brine.ai is the solution to their specific concern.
        5. **CALL TO ACTION**: ALWAYS end by inviting them to book a demo call using this link: https://calendly.com/brine-ai/demo
        6. Keep the tone professional, entrepreneurial, and conversational. Avoid "AI-isms".
        
        Draft the reply email now:
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o", # Using a smarter model for better drafting
                messages=[
                    {"role": "system", "content": "You are a professional B2B sales founder."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error drafting reply: {e}")
            return f"Hi {lead_name},\n\nThank you for your interest! I'd love to chat. Book a call here: https://calendly.com/brine-ai/demo"

if __name__ == "__main__":
    # Test the drafting agent
    agent = DraftingAgent()
    test_query = "This sounds cool. How does this integrate with my CRM? I use Hubspot."
    print("--- DRAFTED REPLY ---")
    print(agent.draft_reply(test_query, "John"))

