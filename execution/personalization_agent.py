#!/usr/bin/env python3
"""
Layer 3: Execution Script
Personalization Agent (Hyper-Personalization)
Analyzes website snippets to generate a custom 'hook' for outreach.
"""

import os
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class PersonalizationAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def generate_hook(self, website_snippet: str, biz_name: str) -> str:
        """
        Generates a 1-sentence personalized opening hook based on website content.
        """
        if not self.client or not website_snippet:
            return ""

        prompt = f"""
        You are an expert sales strategist for Brine.ai. Your task is to write a ONE-SENTENCE personalized opening 'hook' for a cold email.
        
        ### BUSINESS NAME:
        {biz_name}
        
        ### WEBSITE CONTENT SNIPPET:
        {website_snippet}
        
        ### INSTRUCTIONS:
        1. Find a specific "hook" in the text (e.g., a specific service they highlight, a partner's name, an award, a recent project, or a unique value proposition).
        2. Write a professional, congratulatory, or observational opening line.
        3. Examples:
           - "I noticed your firm was recently recognized as a Top 100 Trial Lawyer in Riverside—congratulations!"
           - "I saw that you specialize in niche forensic accounting for high-net-worth individuals, which is a really unique approach."
           - "I was impressed to see that [Name] has been leading your litigation team for over 20 years."
        4. Keep it to exactly ONE sentence.
        5. If you cannot find anything specific, return an empty string.
        
        Personalized Hook:
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional sales writer who avoids 'AI-isms' and sounds human."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )
            hook = response.choices[0].message.content.strip()
            # Clean up quotes if AI adds them
            hook = hook.replace('"', '').replace('\"', '')
            return hook
        except Exception as e:
            print(f"Error generating hook for {biz_name}: {e}")
            return ""

if __name__ == "__main__":
    # Test
    agent = PersonalizationAgent()
    sample_text = "Meier Law Firm is led by founding partner Josh Meier. We recently won the 2023 Excellence in Law award. We focus on personal injury and estate planning in Newport Beach."
    print("--- DRAFTED HOOK ---")
    print(agent.generate_hook(sample_text, "Meier Law Firm"))

