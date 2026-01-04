#!/usr/bin/env python3
"""
Layer 3: Execution Script
Learning Agent (The Recursive Brain)
Analyzes Gmail threads to extract new knowledge and track question frequency.
"""

import os
import json
from typing import Optional, Dict, List, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LearningAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.kb_path = os.path.join(os.path.dirname(__file__), "..", "knowledge_base", "brine_faq.md")
        self.stats_path = os.path.join(os.path.dirname(__file__), "..", "knowledge_base", "learning_stats.json")
        
        # Initialize stats if not exists
        if not os.path.exists(self.stats_path):
            with open(self.stats_path, 'w') as f:
                json.dump({"questions": {}, "unanswered": []}, f)

    def _get_kb_content(self) -> str:
        with open(self.kb_path, 'r') as f:
            return f.read()

    def _update_kb_content(self, new_content: str):
        with open(self.kb_path, 'w') as f:
            f.write(new_content)

    def _get_stats(self) -> Dict[str, Any]:
        with open(self.stats_path, 'r') as f:
            return json.load(f)

    def _save_stats(self, stats: Dict[str, Any]):
        with open(self.stats_path, 'w') as f:
            json.dump(stats, f, indent=4)

    def analyze_thread(self, messages: List[Dict[str, Any]]):
        """
        Reads a thread to find:
        1. Questions asked by the lead.
        2. Answers provided by Isaac (manual replies).
        """
        if not self.client or len(messages) < 2:
            return

        # Prepare thread transcript for AI
        thread_text = ""
        for m in messages:
            sender = m.get('from', 'Unknown')
            body = m.get('body', '')
            thread_text += f"FROM: {sender}\nBODY: {body}\n---\n"

        prompt = f"""
        You are the 'Recursive Brain' for Brine.ai. Your task is to extract knowledge and patterns from this email thread.
        
        ### THREAD TRANSCRIPT:
        {thread_text}
        
        ### CURRENT KNOWLEDGE BASE:
        {self._get_kb_content()}
        
        ### YOUR GOAL:
        1. Identify the CORE QUESTION the lead is asking.
        2. If Isaac (the user) replied manually, extract his answer.
        3. Determine if this question/answer pair is ALREADY in the knowledge base.
        4. If it's NEW or a DIFFERENT way of asking, flag it.
        
        Return your analysis in JSON format:
        {{
            "core_question": "string",
            "is_new_info": bool,
            "isaac_answer": "string or null",
            "suggested_faq_update": "A full Markdown Question/Answer block if this should be added, else null"
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a knowledge synthesis expert. Respond only in JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            analysis = json.loads(response.choices[0].message.content)
            self._process_analysis(analysis)
        except Exception as e:
            print(f"Error in Learning Agent analysis: {e}")

    def _process_analysis(self, analysis: Dict[str, Any]):
        question = analysis.get("core_question")
        if not question: return

        stats = self._get_stats()
        
        # 1. Track Frequency
        if question in stats["questions"]:
            stats["questions"][question]["count"] += 1
        else:
            stats["questions"][question] = {"count": 1, "status": "monitored"}

        # 2. Handle New Info (Isaac's manual wisdom)
        if analysis.get("is_new_info") and analysis.get("suggested_faq_update"):
            print(f"🧠 RECURSIVE BRAIN: Detected new knowledge! Updating FAQ...")
            current_kb = self._get_kb_content()
            new_kb = current_kb + "\n\n" + analysis["suggested_faq_update"]
            self._update_kb_content(new_kb)
            stats["questions"][question]["status"] = "learned"

        # 3. Track unanswered/frequent gaps
        if not analysis.get("isaac_answer") and not analysis.get("is_new_info"):
            if question not in stats["unanswered"]:
                stats["unanswered"].append(question)

        self._save_stats(stats)

    def generate_knowledge_gap_report(self) -> str:
        """
        Generates a summary of unanswered questions and frequently asked topics
        that are not in the knowledge base.
        """
        stats = self._get_stats()
        unanswered = stats.get("unanswered", [])
        questions = stats.get("questions", {})
        
        if not unanswered and not questions:
            return "No knowledge gaps identified this week."

        report = "### 🧠 BRINE.AI KNOWLEDGE GAP REPORT\n\n"
        
        if unanswered:
            report += "#### ⚠️ UNANSWERED QUESTIONS (Manual Review Needed):\n"
            for q in unanswered[:10]: # Top 10
                count = questions.get(q, {}).get("count", 1)
                report += f"- **{q}** (Asked {count} times)\n"
            report += "\n"

        report += "#### 📈 FREQUENT TOPICS:\n"
        # Sort questions by count
        sorted_qs = sorted(questions.items(), key=lambda x: x[1]['count'], reverse=True)
        for q, data in sorted_qs[:5]:
            status = data.get("status", "monitored")
            report += f"- {q}: {data['count']} hits ({status})\n"
            
        report += "\n#### 💡 RECOMMENDATION:\n"
        if unanswered:
            report += "Review the unanswered questions above and add your manual replies to `brine_faq.md` so the agent can handle them automatically next time."
        else:
            report += "Your knowledge base is performing well! No critical gaps found."
            
        return report

if __name__ == "__main__":
    # Small test
    agent = LearningAgent()
    print("Learning Agent initialized.")

