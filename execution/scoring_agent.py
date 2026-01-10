#!/usr/bin/env python3
"""
Layer 3: Execution Script
Lead Scoring Agent (Automation Readiness Audit)
Analyzes business data and "Automation Gaps" to score leads.
"""

import os
import json
from typing import Optional, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ScoringAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def score_lead(self, biz_name: str, reviews_count: int, rating: float, markdown_dna: str = "", automation_gaps: list = []) -> Dict[str, Any]:
        """
        Analyzes business signals and "Automation Gaps" to provide a score from 1-10.
        Higher score = Higher need for AI automation.
        """
        if not self.client:
            return {"score": 5, "reason": "No AI API key available for scoring."}

        prompt = f"""
        You are a strategic sales consultant for Brine.ai, an AI automation agency.
        Your goal is to score a business from 1 to 10 based on how much they NEED automation to scale.

        ### HIGH-VALUE INDUSTRIES (Give +2 to +3 bonus points):
        These industries have high Customer Lifetime Value ($15k-$100k+) and operational pain:
        1. **Solar Panel Installers** - $15k-$30k LTV, compete for shared leads, need exclusive leads
        2. **Roofing & HVAC Contractors (Commercial)** - $20k-$100k+ contracts, miss hot leads while in field
        3. **Personal Injury & Estate Attorneys** - Six-figure settlements, flooded with junk inquiries
        4. **Custom Pool Builders & Renovators** - $50k+ projects, high volume but low tech
        5. **Managed IT & Cybersecurity Firms (MSPs)** - High-ticket recurring contracts, understand automation
        6. **Medical Spas & Regenerative Medicine** - High-margin packages, leads ghost easily
        7. **Specialized CPAs (R&D Tax Credits)** - $5k-$20k fees, need educational outreach at scale

        ### SCORING STRATEGY: SME Growth & Automation Gaps
        **High Score (8-10): "High Value, Low Tech"**
        - Review Count: 50 to 500+. (Stable business, high customer volume, proven budget).
        - **OR**: If review count is 0 but they're from a verified B2B lead source (like Apollo), assume they're a legitimate business and score based on industry + automation gaps.
        - Automation Gaps: {automation_gaps} (Specific things they are MISSING).
        - **HIGH-VALUE INDUSTRY BONUS**: If they're in one of the 7 high-value industries above, add +2 to +3 points.
        - Signals: If they are a busy service business (HVAC, Law, Medical, Solar, Pool, MSP) but lack online booking or a chat widget, they are a PERFECT 10.
        - **B2B Lead Source Bonus**: If review_count is 0 but they have a website and email, they're likely a legitimate B2B lead (not a Google Maps business). Don't penalize for 0 reviews - score based on industry value and automation gaps instead.

        **Medium Score (4-7):**
        - Review Count: 10 to 50. (Growing, but might have smaller budgets).
        - **OR**: Review Count 0 but in a high-value industry with automation gaps.
        - Has some automation (e.g., already has a basic booking widget).
        - May be in a high-value industry but has some automation already.

        **Low Score (1-3):**
        - Very new businesses (under 10 reviews) AND not in a high-value industry AND no automation gaps.
        - Already has high-end automation (AI bots, complex intake systems).
        - Low-ticket businesses with no automation pain.

        ### HEAT SIGNALS (Prioritize These):
        1. **Revenue Potential**: High ticket price ($2,000+) means one close = 10x ROI
        2. **Operational Pain**: Owner-operated or small teams feel manual outreach pain most
        3. **Low Tech Maturity**: Great reviews but slow, non-automated website = "Low-Hanging Fruit"

        ### BUSINESS DATA:
        Name: {biz_name}
        Review Count: {reviews_count}
        Rating: {rating}
        Automation Gaps Found: {automation_gaps}
        Website DNA: {markdown_dna[:1000]}

        ### INSTRUCTION:
        1. First, identify if this business is in one of the 7 high-value industries (Solar, Commercial Roofing/HVAC, Legal, Pool Builders, MSPs, Medical Spas, Specialized CPAs).
        2. **IMPORTANT**: If review_count is 0, this is likely a B2B lead (not a Google Maps business). Don't penalize for 0 reviews. Score based on industry value and automation gaps instead.
        3. Evaluate the "Automation Readiness" based on review count (if > 0), automation gaps, and tech maturity.
        4. If they're in a high-value industry AND have automation gaps, they should score 7-10 (even with 0 reviews if they're from a verified B2B source).
        5. If review_count is 0 but they're in a high-value industry with automation gaps, score them 7-9 (don't penalize for missing reviews).
        6. Combine industry knowledge with existing scoring criteria (reviews, gaps, etc.).

        Return your response in JSON format:
        {{
            "score": <int 1-10>,
            "reason": "<1-sentence explanation focusing on why their high volume vs. missing tech makes them a prime candidate. If they're in a high-value industry, mention that.>"
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a senior sales strategist. Respond only in JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            return {
                "score": data.get("score", 5),
                "reason": data.get("reason", "Could not determine reason.")
            }
        except Exception as e:
            print(f"Error scoring lead {biz_name}: {e}")
            return {"score": 5, "reason": "AI scoring error."}

if __name__ == "__main__":
    # Test
    agent = ScoringAgent()
    print(agent.score_lead("Busy Local HVAC", 250, 4.8, "We handle 500 calls a month manually.", ["No Online Booking"]))
