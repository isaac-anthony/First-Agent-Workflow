#!/usr/bin/env python3
"""
Layer 3: Execution Script
Sentiment Analyzer using OpenAI (ChatGPT)
Classifies lead responses as Interested, Not Interested, or Neutral.
Optimized for high-confidence classification and minimizing ambiguity.
"""

import os
from typing import Literal, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class SentimentAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def classify_response(self, text: str) -> Literal["Interested", "Not Interested", "Neutral", "Unclear"]:
        """
        Uses ChatGPT to classify the sentiment of a lead's response.
        Highly trained to recognize polite rejections and minimize neutral outcomes.
        """
        if not self.client:
            print("WARNING: OPENAI_API_KEY missing. Cannot classify sentiment.")
            return "Unclear"

        prompt = f"""
        You are an expert sales sentiment analyzer for Brine.ai. Your goal is to classify lead responses into exactly three categories. 
        You must be decisive and minimize the use of "Neutral".

        ### CATEGORY 1: "Interested"
        - The lead says yes to a meeting, call, or demo.
        - The lead asks positive follow-up questions ("What are your rates?", "How long does it take?").
        - The lead expresses a current pain point ("We are struggling with this," "We need more efficiency").
        - The lead gives a soft yes ("Maybe next week," "Let's touch base soon").

        ### CATEGORY 2: "Not Interested"
        - Explicit No: "No," "Not interested," "Stop."
        - Polite Rejections: "I'm good but thank you," "We're all set," "No thanks," "Thanks for reaching out but we're not looking."
        - Resource Rejections: "We do this in-house," "We already have a tool," "No budget."
        - Timing Rejections: "Not right now," "Check back in a year," "Too busy."
        - Unsubscribe requests: "Remove me," "Take me off your list."

        ### CATEGORY 3: "Neutral"
        - ONLY use this for: 
            1. Automated out-of-office replies.
            2. Purely technical questions without sentiment ("Is this an automated email?", "Who is this?").
            3. Responses that are literally gibberish or empty.

        ### INSTRUCTION:
        If a response is a polite "No" or a soft rejection like "I'm good," you MUST classify it as "Not Interested". Do not classify polite rejections as "Neutral".

        Lead Response:
        \"\"\"{text}\"\"\"

        Respond with ONLY one word: "Interested", "Not Interested", or "Neutral".
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a decisive sales sentiment analyzer. You accurately detect polite rejections as 'Not Interested'."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=10
            )
            category = response.choices[0].message.content.strip().replace('"', '').replace('.', '')
            if category in ["Interested", "Not Interested", "Neutral"]:
                return category
            return "Unclear"
        except Exception as e:
            print(f"Error classifying sentiment: {e}")
            return "Unclear"
