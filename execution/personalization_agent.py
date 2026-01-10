#!/usr/bin/env python3
"""
Layer 3: Execution Script
Personalization Agent (The "Golden Nugget" Finder)
Analyzes Markdown website DNA to find psychological hooks.
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

    def generate_hook(self, markdown_dna: str, biz_name: str) -> str:
        """
        Generates a 1-sentence personalized opening hook based on "Golden Nuggets" in the Markdown.
        """
        if not self.client or not markdown_dna:
            return ""

        prompt = f"""
        You are a lead generation strategist for Brine.ai. Your task is to find "Golden Nuggets" in the provided Markdown content of a business website and write ONE high-converting personalized opening hook.

        ### BUSINESS NAME:
        {biz_name}

        ### WEBSITE MARKDOWN DNA:
        {markdown_dna}

        ### HIGH-VALUE INDUSTRIES & THEIR PAIN POINTS:
        If you identify this business is in one of these industries, craft hooks that address their specific pain:
        
        1. **Solar Panel Installers**: Focus on "exclusive leads" vs. shared leads. Mention cost savings from not competing with 5 other companies.
        2. **Roofing/HVAC (Commercial)**: Focus on "Speed-to-Lead" for field workers. Mention never missing a hot lead while on a job site.
        3. **Personal Injury Attorneys**: Focus on "Qualification Shield" for filtering junk. Mention reducing paralegal costs by pre-qualifying leads.
        4. **Pool Builders**: Focus on "Solution Architect" - technical bridge to growth. Mention modernizing without disrupting operations.
        5. **MSPs (IT/Cybersecurity)**: Focus on "Peer-to-peer" - selling automation to those who sell automation. Mention they understand automation but need help with their own sales.
        6. **Medical Spas**: Focus on "Preventing lead ghosting" with multi-stage follow-up. Mention immediate response and nurturing.
        7. **Specialized CPAs (R&D Tax Credits)**: Focus on "Educational outreach at scale". Mention complex services need explanation.

        ### MISSION:
        Find a specific detail that proves a human spent 10 minutes on their site. Prioritize in this order:
        1. **Specific People:** Mention an owner, founder, or key team member by name and a detail about their role or history.
        2. **Niche Specialization:** Mention a highly specific service they offer that isn't just generic (e.g., "radiant floor heating" vs "HVAC").
        3. **Awards/Longevity:** Mention a specific award (e.g., "Best of Riverside 2023") or how long they've been in the community.
        4. **Industry-Specific Pain:** If you identify they're in a high-value industry, subtly reference their pain point (e.g., "I noticed you're often in the field" for commercial HVAC).

        ### GUIDELINES:
        - Exactly ONE sentence.
        - NO "AI-isms" (e.g., "I noticed your website," "I was intrigued by," "In today's landscape").
        - NO em-dashes or asterisks. Use commas or periods instead.
        - Must sound like a professional peer-to-peer observation.
        - If they're in a high-value industry, weave in their pain point naturally (don't be obvious).
        
        ### EXAMPLES BY INDUSTRY:
        - **Legal**: "I was impressed to see that Josh Meier has been leading your litigation team in Newport Beach for over two decades, congratulations on that longevity!"
        - **HVAC**: "I noticed that you specifically specialize in energy-efficient hydronic heating systems, which is such a unique value proposition for the Orange County area."
        - **Solar**: "I saw that you're competing for shared leads on Angi, what if you had exclusive, pre-qualified leads instead?"
        - **Commercial Roofing**: "I noticed you're often in the field on commercial projects, what if your AI handled lead qualification so you never miss a hot opportunity?"
        - **Medical Spa**: "I saw you offer high-value treatments like CoolSculpting, what if AI could ensure no lead goes cold with immediate, personalized follow-up?"

        Personalized Hook:
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o", # Using GPT-4o for deeper psychological profiling
                messages=[
                    {"role": "system", "content": "You are a senior sales consultant. Your tone is direct, professional, and human."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            hook = response.choices[0].message.content.strip()
            # Clean up special characters that might trigger different fonts/colors
            hook = hook.replace('"', '').replace('\"', '').replace('**', '').replace('—', ',')
            return hook
        except Exception as e:
            print(f"Error generating hook for {biz_name}: {e}")
            return ""

if __name__ == "__main__":
    # Test
    agent = PersonalizationAgent()
    sample_md = "### PAGE: About\nMeier Law Firm is led by founding partner Josh Meier. He has practiced law for 25 years. We focus on personal injury."
    print("--- DRAFTED HOOK ---")
    print(agent.generate_hook(sample_md, "Meier Law Firm"))
