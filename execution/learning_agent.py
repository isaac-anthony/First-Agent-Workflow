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
        self.qa_db_path = os.path.join(os.path.dirname(__file__), "..", "knowledge_base", "question_learning.json")
        
        # Initialize stats if not exists
        if not os.path.exists(self.stats_path):
            with open(self.stats_path, 'w') as f:
                json.dump({"questions": {}, "unanswered": []}, f)
        
        # Initialize Q&A database if not exists
        if not os.path.exists(self.qa_db_path):
            with open(self.qa_db_path, 'w') as f:
                json.dump({"qa_pairs": [], "confidence_scores": {}}, f)

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

    def analyze_question(self, question_text: str, thread_id: str = None, manual_answer: str = None):
        """
        Analyzes a question and learns from manual answers.
        Stores question-answer pairs for future reference and confidence improvement.
        """
        if not self.client:
            return
        
        # Load Q&A database
        try:
            with open(self.qa_db_path, 'r') as f:
                qa_db = json.load(f)
        except:
            qa_db = {"qa_pairs": [], "confidence_scores": {}}
        
        # Analyze question
        prompt = f"""
        You are analyzing a question from a lead to improve the knowledge base.
        
        ### QUESTION:
        "{question_text}"
        
        ### MANUAL ANSWER (if provided):
        {manual_answer if manual_answer else "No manual answer yet - this is a new question"}
        
        ### EXISTING Q&A DATABASE:
        {json.dumps(qa_db['qa_pairs'][-5:], indent=2) if qa_db['qa_pairs'] else "No previous Q&A pairs"}
        
        ### YOUR TASK:
        1. Extract the core question (normalized form)
        2. If manual_answer is provided, store the Q&A pair
        3. Determine if this question is similar to any existing questions
        4. Calculate confidence that we can answer this based on knowledge base
        
        Return JSON:
        {{
            "core_question": "<normalized question>",
            "question_type": "<pricing|technical|capability|process|comparison|general>",
            "has_answer": <bool>,
            "confidence": <float 0.0-1.0>,
            "similar_questions": ["<list of similar questions if any>"]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a knowledge management expert. Respond only in JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            analysis = json.loads(response.choices[0].message.content)
            
            # Store Q&A pair if manual answer provided
            if manual_answer:
                qa_pair = {
                    "question": analysis.get("core_question", question_text),
                    "answer": manual_answer,
                    "question_type": analysis.get("question_type", "general"),
                    "thread_id": thread_id,
                    "timestamp": str(os.path.getmtime(self.qa_db_path) if os.path.exists(self.qa_db_path) else "")
                }
                qa_db["qa_pairs"].append(qa_pair)
                
                # Update confidence score for this question type
                q_type = analysis.get("question_type", "general")
                if q_type not in qa_db["confidence_scores"]:
                    qa_db["confidence_scores"][q_type] = []
                qa_db["confidence_scores"][q_type].append(1.0)  # Manual answer = 100% confidence
                
                # Save updated database
                with open(self.qa_db_path, 'w') as f:
                    json.dump(qa_db, f, indent=4)
                
                print(f"🧠 Learned new Q&A pair: {analysis.get('core_question', question_text)[:50]}...")
            
            return analysis
        except Exception as e:
            print(f"Error analyzing question: {e}")
            return None

    def get_confidence_for_question(self, question_text: str) -> float:
        """
        Gets confidence score for answering a question based on learned Q&A pairs.
        Returns confidence (0.0-1.0) based on similar questions in database.
        """
        try:
            with open(self.qa_db_path, 'r') as f:
                qa_db = json.load(f)
        except:
            return 0.5  # Default medium confidence
        
        # Check if similar questions exist in database
        similar_count = 0
        total_confidence = 0.0
        
        for qa_pair in qa_db.get("qa_pairs", []):
            # Simple similarity check (can be enhanced with embeddings)
            if any(word in question_text.lower() for word in qa_pair["question"].lower().split()[:5]):
                similar_count += 1
                total_confidence += 1.0
        
        if similar_count > 0:
            return min(1.0, total_confidence / max(1, similar_count))
        
        return 0.5  # Default if no similar questions found

if __name__ == "__main__":
    # Small test
    agent = LearningAgent()
    print("Learning Agent initialized.")

