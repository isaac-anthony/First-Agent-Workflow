#!/usr/bin/env python3
"""
Question Detection Agent
Detects if a reply contains questions and identifies question types.
"""

import os
import json
from typing import Optional, Dict, List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class QuestionDetector:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def detect_questions(self, text: str) -> Dict:
        """
        Detects if text contains questions and identifies question types.
        
        Returns:
            {
                "has_questions": bool,
                "questions": [{"question": str, "type": str, "confidence": float}],
                "question_count": int
            }
        """
        if not self.client:
            return {"has_questions": False, "questions": [], "question_count": 0}

        prompt = f"""
        You are a question detection expert. Analyze the following text to identify if it contains questions.
        
        ### TEXT TO ANALYZE:
        "{text}"
        
        ### YOUR TASK:
        1. Identify ALL questions in the text (explicit questions with "?", implicit questions, or statements that are clearly asking for information).
        2. Categorize each question by type:
           - "pricing" - Questions about cost, pricing, payment plans
           - "technical" - Questions about how it works, integrations, features
           - "capability" - Questions about what the service can do
           - "process" - Questions about onboarding, timeline, deployment
           - "comparison" - Questions comparing to other solutions
           - "general" - Other questions
        
        3. Rate your confidence that each is actually a question (0.0 to 1.0).
        
        Return your response in JSON format:
        {{
            "has_questions": <bool>,
            "questions": [
                {{
                    "question": "<the exact question text>",
                    "type": "<pricing|technical|capability|process|comparison|general>",
                    "confidence": <float 0.0-1.0>
                }}
            ],
            "question_count": <int>
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a question detection expert. Respond only in JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            return {
                "has_questions": data.get("has_questions", False),
                "questions": data.get("questions", []),
                "question_count": data.get("question_count", 0)
            }
        except Exception as e:
            print(f"Error detecting questions: {e}")
            return {"has_questions": False, "questions": [], "question_count": 0}

if __name__ == "__main__":
    # Test
    detector = QuestionDetector()
    test_text = "This sounds interesting. How much does it cost? And can it integrate with HubSpot?"
    result = detector.detect_questions(test_text)
    print("Question Detection Test:")
    print(f"Has Questions: {result['has_questions']}")
    print(f"Question Count: {result['question_count']}")
    for q in result['questions']:
        print(f"  - {q['question']} (Type: {q['type']}, Confidence: {q['confidence']})")

