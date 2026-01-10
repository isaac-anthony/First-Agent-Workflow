#!/usr/bin/env python3
"""
Layer 3: Execution Script
Reporting Agent
Aggregates performance metrics and generates a professional weekly executive report.
Refined for small business weighted pipeline potential.
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from google_sheets_client import GoogleSheetsClient
from learning_agent import LearningAgent
from send_onboarding_email import send_basic_email
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

import asyncio
from playwright.async_api import async_playwright

class ReportingAgent:
    def __init__(self):
        self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
        self.sheets = GoogleSheetsClient(self.spreadsheet_id)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.learner = LearningAgent()
        self.recipient = os.getenv("REPORT_EMAIL", "04isaacag@gmail.com")

    async def _generate_pdf(self, html_content: str, output_path: str):
        """Generates a PDF from HTML content using Playwright."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_content(html_content)
            # Wait for any dynamic content/styles to load
            await page.wait_for_timeout(1000)
            await page.pdf(path=output_path, format="A4", margin={"top": "20px", "bottom": "20px", "left": "20px", "right": "20px"})
            await browser.close()

    def aggregate_weekly_stats(self) -> Dict[str, Any]:
        """Scans all lead tabs and aggregates metrics."""
        all_tabs = self.sheets.get_sheet_names()
        
        stats = {
            "total_leads": 0,
            "total_contacted": 0,
            "total_interested": 0,
            "total_rejected": 0,
            "avg_ai_score": 0.0,
            "pipeline_potential": 0,
            "niche_breakdown": {}
        }
        
        scores = []
        
        # Focus on Sheet2 (main lead sheet)
        target_tabs = ["Sheet2"] if "Sheet2" in all_tabs else [tab for tab in all_tabs if tab not in ["Weekly_Reports", "Sheet1"]]
        
        for tab in target_tabs:
            rows = self.sheets.get_all_values(tab)
            if not rows or len(rows) <= 1: continue
            
            headers = rows[0]
            data = rows[1:]
            
            try:
                col_contacted = headers.index("Contacted?")
                col_status = headers.index("Status")
                col_score = headers.index("AI Lead Score")
            except ValueError:
                # Try alternative column names
                try:
                    col_contacted = headers.index("Contacted")
                    col_status = headers.index("Status")
                    col_score = headers.index("Score")
                except ValueError:
                    continue # Skip tabs that don't match the lead format
            
            tab_interested = 0
            for row in data:
                stats["total_leads"] += 1
                
                # Check if contacted
                is_contacted = len(row) > col_contacted and str(row[col_contacted]).lower() == "yes"
                if is_contacted:
                    stats["total_contacted"] += 1
                
                # Check interest status
                status = str(row[col_status]).lower() if len(row) > col_status else ""
                score = int(row[col_score]) if len(row) > col_score and str(row[col_score]).isdigit() else 5
                
                if "interested" in status:
                    stats["total_interested"] += 1
                    tab_interested += 1
                    # Weighted Pipeline Calculation: Score 10 = $1,000, Score 4 = $400
                    stats["pipeline_potential"] += (score / 10) * 1000
                elif "archived" in status:
                    stats["total_rejected"] += 1
                
                if len(row) > col_score and str(row[col_score]).isdigit():
                    scores.append(int(row[col_score]))
            
            stats["niche_breakdown"][tab] = {"total": len(data), "interested": tab_interested}

        if scores:
            stats["avg_ai_score"] = round(sum(scores) / len(scores), 1)
        
        # Round pipeline potential
        stats["pipeline_potential"] = round(stats["pipeline_potential"], 2)
        
        return stats

    def generate_executive_summary(self, stats: Dict[str, Any]) -> str:
        """Uses AI to write a professional summary of the week's performance."""
        if not self.client:
            return "Executive summary unavailable: OpenAI API key missing."

        prompt = f"""
        You are the Chief Sales Officer for Brine.ai. Write a professional, high-level executive summary for the CEO (Isaac).
        
        WEEKLY STATS:
        - Total Leads Found: {stats['total_leads']}
        - Total Contacted: {stats['total_contacted']}
        - Positive Replies/Interest: {stats['total_interested']}
        - Weighted Pipeline Potential: ${stats['pipeline_potential']}
        - Average Lead Quality (AI Score): {stats['avg_ai_score']}/10
        - Niche Performance: {json.dumps(stats['niche_breakdown'])}
        
        INSTRUCTIONS:
        1. Keep it professional and strategic.
        2. Highlight which niche is the 'Sweet Spot' (High volume vs Low Tech).
        3. Mention the value of focusing on small teams (2-5 people) who are the sole decision-makers.
        4. End with a "Strategic Recommendation" for next week (e.g., focus more on HVAC/Home Services).
        5. Use a clean, executive tone.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def run_weekly_report(self):
        print("--- GENERATING WEEKLY REPORT ---")
        stats = self.aggregate_weekly_stats()
        summary = self.generate_executive_summary(stats)
        
        # Fetch Knowledge Gap report if it's Friday (or if run manually)
        knowledge_gap = ""
        if datetime.now().weekday() == 4 or True: # Force for now so user can see it
            knowledge_gap = self.learner.generate_knowledge_gap_report()

        # Generate Email HTML Body
        gap_content = ""
        if knowledge_gap:
            formatted_gap = knowledge_gap.replace('### ', '').replace('#### ', '<strong>').replace('\n', '<br>')
            gap_content = f"""
                <h3 style="color: #c0392b;">🧠 Knowledge Gap Report:</h3>
                <div style="background: #fff5f5; padding: 15px; border-left: 4px solid #c0392b; white-space: pre-wrap;">
                    {formatted_gap}
                </div>
            """

        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 10px;">Brine.ai Weekly Performance Report</h2>
                <p><strong>Week Ending:</strong> {datetime.now().strftime("%B %d, %Y")}</p>
                
                <div style="background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #2c3e50;">Key Metrics:</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr><td><strong>Total Leads Scanned:</strong></td><td style="text-align: right;">{stats['total_leads']}</td></tr>
                        <tr><td><strong>Total Outreach Sent:</strong></td><td style="text-align: right;">{stats['total_contacted']}</td></tr>
                        <tr><td><strong>Interest Detected:</strong></td><td style="text-align: right; color: #27ae60;">{stats['total_interested']}</td></tr>
                        <tr><td><strong>Avg. Lead Quality:</strong></td><td style="text-align: right;">{stats['avg_ai_score']}/10</td></tr>
                        <tr style="font-size: 1.2em; border-top: 1px solid #ccc;">
                            <td style="padding-top: 10px;"><strong>Weighted Pipeline Potential:</strong></td>
                            <td style="padding-top: 10px; text-align: right; color: #2980b9;"><strong>${stats['pipeline_potential']:,}</strong></td>
                        </tr>
                    </table>
                    <p style="font-size: 0.8em; color: #666; margin-top: 10px;">*Weighted based on AI Score (Score 10 = $1,000)*</p>
                </div>

                <h3 style="color: #2c3e50;">Executive Summary:</h3>
                <div style="white-space: pre-wrap; background: #fff; padding: 10px; border-left: 4px solid #2c3e50;">
                    {summary}
                </div>

                {gap_content}

                <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="font-size: 0.8em; color: #777; text-align: center;">
                    <em>This report was automatically generated by your Brine.ai Agentic Sales Engine.</em>
                </p>
            </div>
        </body>
        </html>
        """

        # 1. Update Google Sheet (Weekly_Reports Tab)
        report_row = [
            datetime.now().strftime("%Y-%m-%d"),
            stats['total_leads'],
            stats['total_contacted'],
            stats['total_interested'],
            stats['pipeline_potential'],
            stats['avg_ai_score'],
            summary + ("\n\n" + knowledge_gap if knowledge_gap else "")
        ]
        
        self.sheets.initialize_report_sheet()
        self.sheets.append_leads([report_row], tab_name="Weekly_Reports")
        
        # 2. Send Email to Isaac
        result = send_basic_email(
            self.recipient, 
            f"📊 Brine.ai Weekly Report: {datetime.now().strftime('%Y-%m-%d')}", 
            email_body, 
            is_html=True
        )
        
        if result['success']:
            print("SUCCESS: Weekly Report sent and archived in Google Sheets.")
        else:
            print(f"FAILED: Could not send email: {result['message']}")

if __name__ == "__main__":
    agent = ReportingAgent()
    agent.run_weekly_report()
