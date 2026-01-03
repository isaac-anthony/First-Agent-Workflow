#!/usr/bin/env python3
"""
Layer 3: Execution Script
Lead Scoring Agent
Analyzes business data (reviews, description, size) to score leads.
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
        """
        if not self.client:
            return {"score": 5, "reason": "No AI API key available for scoring."}

        prompt = f"""
        You are a B2B lead qualification expert. Your goal is to score a business from 1 to 10 based on its potential as a client for an AI automation agency (Brine.ai).
        
        High Score (8-10): 
        - Established businesses with 10+ employees.
        - High volume of customer interactions (indicated by many reviews).
        - Complex operations that could benefit from automation.
        
        Medium Score (4-7):
        - Moderate reviews (20-50).
        - Standard business operations.
        - Small teams (3-5 people).
        
        Low Score (1-3):
        - Solo-operators or very small businesses.
        - Very few reviews (under 10).
        - Low complexity operations.
        
        BUSINESS DATA:
        Name: {biz_name}
        Review Count: {reviews_count}
        Rating: {rating}
        Description/Snippets: {description}
        
        ### INSTRUCTION:
        Evaluate the likelihood that this business has 5+ employees and complex enough operations to afford a $1,000+/mo automation service.
        
        Return your response in JSON format like this:
        {{
            "score": <int 1-10>,
            "reason": "<1-sentence explanation of the score>"
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a lead qualification expert. Respond only in JSON."},
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
    print(agent.score_lead("Big Law Firm LLP", 150, 4.8, "Top tier litigation and corporate law firm with multiple locations."))
    print(agent.score_lead("Solo Plumber John", 2, 5.0, "Individual plumber doing residential repairs."))

