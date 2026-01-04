#!/usr/bin/env python3
"""
Layer 3: Execution Script
Lead Scoring Agent
Analyzes business data (reviews, description, size) to score leads.
Refined for small business automation (10-50 reviews = High Quality).
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

    def score_lead(self, biz_name: str, reviews_count: int, rating: float, description: str = "") -> Dict[str, Any]:
        """
        Analyzes business signals to provide a score from 1-10.
        Prioritizes 'High Volume vs Low Tech' - the small business sweet spot.
        """
        if not self.client:
            return {"score": 5, "reason": "No AI API key available for scoring."}

        prompt = f"""
        You are a lead qualification expert for Brine.ai, an AI automation agency.
        Your goal is to score a business from 1 to 10 based on how much they NEED automation.
        
        ### SCORING STRATEGY: Small Business Sweet Spot
        We are looking for "High Volume vs. Low Tech" businesses.
        
        High Score (8-10): "The Breaking Point"
        - Review Count: 10 to 50 reviews. (This indicates they are busy enough to have customers, but likely overwhelmed and still handling things manually).
        - Solo-operators or Small Teams (2-5 people). (AI is a replacement for a full-time hire they can't afford yet. They are the sole decision-makers).
        - High-frequency niches (HVAC, Plumbing, CPAs, Restaurants).
        
        Medium Score (4-7):
        - Established firms with 100+ reviews. (They likely already have dedicated office managers or software systems in place).
        - Rating is very high, but growth is stagnant.
        
        Low Score (1-3):
        - Very new businesses (0-5 reviews).
        - No website or very low complexity operations.
        
        BUSINESS DATA:
        Name: {biz_name}
        Review Count: {reviews_count}
        Rating: {rating}
        Description/Snippets: {description}
        
        ### INSTRUCTION:
        Evaluate if this business is at the "Breaking Point" where an AI Agent could replace a manual workflow. Solo-operators and small teams with 10-50 reviews are the HIGHEST quality.
        
        Return your response in JSON format like this:
        {{
            "score": <int 1-10>,
            "reason": "<1-sentence explanation of why they are at the breaking point or why they are lower priority>"
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o", # Using gpt-4o for better strategic reasoning
                messages=[
                    {"role": "system", "content": "You are a strategic sales consultant. Respond only in JSON."},
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
    print(agent.score_lead("Busy Local HVAC", 25, 4.8, "Small family owned heating and air business."))
    print(agent.score_lead("Massive Corporate Law Firm", 500, 4.2, "National firm with 50 locations."))
