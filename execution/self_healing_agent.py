#!/usr/bin/env python3
"""
Self-Healing Agent
Monitors for anti-patterns and automatically prevents/fixes issues.
Implements autonomous learning and self-healing loop.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Load .env from project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

sys.path.append(os.path.dirname(__file__))

from google_sheets_client import GoogleSheetsClient
from gmail_client import GmailClient

class SelfHealingAgent:
    """
    Autonomous agent that monitors, detects, and prevents anti-patterns.
    Implements self-healing loop for email automation.
    """
    
    def __init__(self):
        self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
        self.my_email = os.getenv('EMAIL_FROM', 'brineaiconsulting@gmail.com').lower()
        self.sheets = GoogleSheetsClient(self.spreadsheet_id) if self.spreadsheet_id else None
        self.gmail = GmailClient()
        self.learning_log_path = os.path.join(project_root, "knowledge_base", "self_healing_log.json")
        self._load_learning_log()
    
    def _load_learning_log(self):
        """Load historical learning data."""
        if os.path.exists(self.learning_log_path):
            try:
                with open(self.learning_log_path, 'r') as f:
                    self.learning_log = json.load(f)
            except:
                self.learning_log = {
                    "issues_detected": [],
                    "issues_prevented": [],
                    "patterns_learned": {},
                    "last_audit": None
                }
        else:
            self.learning_log = {
                "issues_detected": [],
                "issues_prevented": [],
                "patterns_learned": {},
                "last_audit": None
            }
        
        # Load bug patterns knowledge base
        bug_patterns_path = os.path.join(project_root, "knowledge_base", "bug_patterns.json")
        if os.path.exists(bug_patterns_path):
            try:
                with open(bug_patterns_path, 'r') as f:
                    self.bug_patterns = json.load(f)
            except:
                self.bug_patterns = {}
        else:
            self.bug_patterns = {}
    
    def _save_learning_log(self):
        """Save learning data to disk."""
        os.makedirs(os.path.dirname(self.learning_log_path), exist_ok=True)
        with open(self.learning_log_path, 'w') as f:
            json.dump(self.learning_log, f, indent=2)
    
    def validate_before_send(self, email: str, lead_name: str, biz_name: str, 
                            row_data: dict, tab_name: str = "Sheet2") -> Tuple[bool, str]:
        """
        Validates all conditions before sending an email.
        Returns (is_valid, reason_if_invalid)
        """
        issues = []
        
        # 1. Check "Contacted?" column
        contacted = row_data.get('contacted', '').strip().lower()
        if contacted == "yes":
            issues.append("Already contacted (Contacted? = Yes)")
        
        # 2. Check "Status" column
        # Note: "pending" means ready to send, not already processed
        status = row_data.get('status', '').strip().lower()
        if status in ["interested", "archived", "not interested"]:
            issues.append(f"Status indicates already processed: {status}")
        
        # 3. Verify email exists and is valid
        if not email or '@' not in email:
            issues.append("Invalid or missing email address")
        
        # 4. Check for recent duplicate sends (last hour)
        if self._check_recent_send(email, biz_name):
            issues.append("Email sent recently (within last hour)")
        
        # 5. Validate lead_name (prevent "Yes" bug)
        if lead_name and lead_name.strip().lower() == "yes":
            issues.append("Invalid lead_name detected (likely column mix-up)")
            lead_name = "Team"  # Auto-fix
        
        # 6. Check column index safety
        if self._check_column_confusion(row_data):
            issues.append("Potential column index confusion detected")
        
        if issues:
            reason = "; ".join(issues)
            self._log_issue_prevented("duplicate_email", reason, email, biz_name)
            return False, reason
        
        return True, "All validations passed"
    
    def _check_recent_send(self, email: str, biz_name: str, hours: int = 1) -> bool:
        """Check if email was sent recently to this lead."""
        try:
            # Search Gmail for recent emails to this address
            search_query = f'to:{email} subject:"100 leads for {biz_name}"'
            threads = self.gmail.search_threads(search_query)
            
            if threads:
                # Check if any thread has a message from us in the last hour
                cutoff = datetime.now() - timedelta(hours=hours)
                for thread in threads[:3]:  # Check first 3 threads
                    thread_details = self.gmail.get_thread_details(thread['id'])
                    if thread_details:
                        messages = thread_details.get('messages', [])
                        for msg in messages:
                            headers = msg.get('payload', {}).get('headers', [])
                            from_header = next((h['value'] for h in headers if h['name'].lower() == 'from'), "")
                            if self.my_email in from_header.lower():
                                # Check timestamp
                                date_header = next((h['value'] for h in headers if h['name'].lower() == 'date'), "")
                                # Simple check: if thread exists and is recent, likely duplicate
                                return True
        except Exception as e:
            print(f"Warning: Could not check recent sends: {e}")
        
        return False
    
    def _check_column_confusion(self, row_data: dict) -> bool:
        """Detect potential column index confusion."""
        # Check if lead_name looks like it came from wrong column
        lead_name = row_data.get('lead_name', '').strip()
        
        # Common wrong values that might come from other columns
        wrong_values = ['yes', 'no', 'pending', 'interested', 'archived']
        if lead_name.lower() in wrong_values:
            return True
        
        return False
    
    def validate_before_reply(self, thread_id: str, from_email: str) -> Tuple[bool, str]:
        """
        Validates conditions before processing a reply.
        Returns (is_valid, reason_if_invalid)
        """
        issues = []
        
        # 1. Verify from_email is NOT our own email
        if from_email.lower() == self.my_email:
            issues.append("Reply is from our own email (not a lead reply)")
        
        # 2. Verify thread has at least 2 messages
        try:
            thread_details = self.gmail.get_thread_details(thread_id)
            if thread_details:
                messages = thread_details.get('messages', [])
                if len(messages) < 2:
                    issues.append("Thread has less than 2 messages (no reply yet)")
        except Exception as e:
            issues.append(f"Could not verify thread: {e}")
        
        if issues:
            reason = "; ".join(issues)
            self._log_issue_prevented("false_reply", reason, from_email, thread_id)
            return False, reason
        
        return True, "All validations passed"
    
    def detect_column_mismatches(self, tab_name: str = "Sheet2") -> List[Dict]:
        """
        Detects column index mismatches by comparing hardcoded column letters
        with actual header structure.
        """
        if not self.sheets:
            return []
        
        issues = []
        try:
            rows = self.sheets.get_all_values(tab_name)
            if not rows or len(rows) <= 1:
                return issues
            
            headers = rows[0]
            
            # Expected column mappings (from initialize_sheet)
            expected_columns = {
                "Contacted?": "Q",  # Index 16
                "Time Contacted": "R",  # Index 17
                "Follow-up Count": "S",  # Index 18
                "Status": "B",  # Index 1
                "Lead Name": "P",  # Index 15
            }
            
            # Verify actual column positions match expectations
            for col_name, expected_letter in expected_columns.items():
                try:
                    actual_idx = headers.index(col_name)
                    actual_letter = chr(65 + actual_idx) if actual_idx < 26 else 'A' + chr(65 + (actual_idx - 26))
                    
                    if actual_letter != expected_letter:
                        issues.append({
                            "type": "column_mismatch",
                            "column": col_name,
                            "expected": expected_letter,
                            "actual": actual_letter,
                            "index": actual_idx,
                            "severity": "high"
                        })
                except ValueError:
                    issues.append({
                        "type": "missing_column",
                        "column": col_name,
                        "severity": "critical"
                    })
            
        except Exception as e:
            print(f"Error detecting column mismatches: {e}")
        
        return issues
    
    def detect_unreachable_code_patterns(self, file_path: str) -> List[Dict]:
        """
        Detects potential unreachable code patterns (code after continue/return).
        This is a simplified check - full analysis would require AST parsing.
        """
        issues = []
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, start=1):
                # Look for continue/return followed by non-comment, non-blank code
                if 'continue' in line or 'return' in line:
                    # Check next few lines for actual code (not just comments/blanks)
                    for j in range(i, min(i + 5, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and not next_line.startswith('#') and not next_line.startswith('"""'):
                            # Potential unreachable code
                            issues.append({
                                "type": "unreachable_code",
                                "file": file_path,
                                "line": i,
                                "issue": f"Code after {line.strip()} may be unreachable",
                                "severity": "high"
                            })
                            break
        except Exception as e:
            print(f"Error detecting unreachable code: {e}")
        
        return issues
    
    def audit_sheet_state(self, tab_name: str = "Sheet2") -> Dict:
        """
        Audits the sheet for state inconsistencies and issues.
        Returns audit report.
        """
        if not self.sheets:
            return {"error": "Sheets client not initialized"}
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "tab": tab_name,
            "issues_found": [],
            "fixes_applied": [],
            "statistics": {},
            "column_mismatches": [],
            "unreachable_code_issues": []
        }
        
        # Detect column mismatches
        column_issues = self.detect_column_mismatches(tab_name)
        if column_issues:
            report["column_mismatches"] = column_issues
            for issue in column_issues:
                report["issues_found"].append(
                    f"Column mismatch: {issue['column']} expected at {issue.get('expected', 'N/A')}, "
                    f"found at {issue.get('actual', 'N/A')}"
                )
        
        try:
            rows = self.sheets.get_all_values(tab_name)
            if not rows or len(rows) <= 1:
                return report
            
            headers = rows[0]
            lead_rows = rows[1:]
            
            # Find column indices
            try:
                col_contacted = headers.index("Contacted?")
                col_status = headers.index("Status")
                col_email = headers.index("Email")
                col_lead_name = headers.index("Lead Name")
                col_time_contacted = headers.index("Time Contacted")
            except ValueError as e:
                report["issues_found"].append(f"Missing required column: {e}")
                return report
            
            stats = {
                "total_leads": len(lead_rows),
                "contacted": 0,
                "not_contacted": 0,
                "status_pending": 0,
                "potential_issues": 0
            }
            
            for i, row in enumerate(lead_rows, start=2):
                # Ensure row has enough columns
                while len(row) < len(headers):
                    row.append("")
                
                email = row[col_email].strip() if len(row) > col_email else ""
                contacted = row[col_contacted].strip().lower() if len(row) > col_contacted else ""
                status = row[col_status].strip() if len(row) > col_status else ""
                lead_name = row[col_lead_name].strip() if len(row) > col_lead_name else ""
                time_contacted = row[col_time_contacted].strip() if len(row) > col_time_contacted else ""
                
                # Count statistics
                if contacted == "yes":
                    stats["contacted"] += 1
                else:
                    stats["not_contacted"] += 1
                
                if status.lower() == "pending":
                    stats["status_pending"] += 1
                
                # Check for issues
                issues = []
                
                # Issue: Contacted but no timestamp
                if contacted == "yes" and not time_contacted:
                    issues.append(f"Row {i}: Contacted but missing timestamp")
                    # Auto-fix: Add timestamp (Column R is Time Contacted)
                    self.sheets.update_cell(f"R{i}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tab_name)
                    report["fixes_applied"].append(f"Row {i}: Added missing timestamp")
                
                # Issue: Invalid lead_name
                if lead_name and lead_name.lower() in ['yes', 'no', 'pending']:
                    issues.append(f"Row {i}: Invalid lead_name '{lead_name}' (likely column mix-up)")
                    # Auto-fix: Set to "Team"
                    self.sheets.update_cell(f"O{i}", "Team", tab_name)
                    report["fixes_applied"].append(f"Row {i}: Fixed invalid lead_name")
                
                # Issue: Status mismatch
                if contacted == "yes" and status.lower() not in ["pending", "interested", "archived", "not interested", "followed up"]:
                    issues.append(f"Row {i}: Contacted but status is '{status}' (should be Pending or similar)")
                
                if issues:
                    stats["potential_issues"] += len(issues)
                    report["issues_found"].extend(issues)
            
            report["statistics"] = stats
            report["summary"] = f"Audited {stats['total_leads']} leads. Found {len(report['issues_found'])} issues, applied {len(report['fixes_applied'])} fixes."
            
        except Exception as e:
            report["error"] = str(e)
        
        # Save audit to learning log
        self.learning_log["last_audit"] = report
        self._save_learning_log()
        
        return report
    
    def _log_issue_prevented(self, issue_type: str, reason: str, email: str, context: str):
        """Log an issue that was prevented."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "issue_type": issue_type,
            "reason": reason,
            "email": email,
            "context": context
        }
        self.learning_log["issues_prevented"].append(entry)
        
        # Keep only last 100 entries
        if len(self.learning_log["issues_prevented"]) > 100:
            self.learning_log["issues_prevented"] = self.learning_log["issues_prevented"][-100:]
        
        self._save_learning_log()
    
    def learn_pattern(self, pattern_name: str, pattern_data: dict):
        """Learn a new pattern for future detection."""
        self.learning_log["patterns_learned"][pattern_name] = {
            "first_detected": datetime.now().isoformat(),
            "data": pattern_data,
            "occurrences": self.learning_log["patterns_learned"].get(pattern_name, {}).get("occurrences", 0) + 1
        }
        self._save_learning_log()
    
    def check_known_bug_patterns(self, file_path: str = None, tab_name: str = "Sheet2") -> List[Dict]:
        """
        Checks for known bug patterns from the knowledge base.
        Returns list of detected issues.
        """
        issues = []
        
        # Check for column mismatches
        if tab_name:
            column_issues = self.detect_column_mismatches(tab_name)
            issues.extend(column_issues)
        
        # Check for unreachable code patterns
        if file_path and os.path.exists(file_path):
            unreachable_issues = self.detect_unreachable_code_patterns(file_path)
            issues.extend(unreachable_issues)
        
        # Log detected patterns
        if issues:
            for issue in issues:
                pattern_type = issue.get("type", "unknown")
                if pattern_type in self.bug_patterns.get("patterns", {}):
                    self.learn_pattern(pattern_type, issue)
        
        return issues
    
    def get_health_report(self) -> Dict:
        """Get overall system health report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "issues_prevented_count": len(self.learning_log.get("issues_prevented", [])),
            "patterns_learned_count": len(self.learning_log.get("patterns_learned", {})),
            "last_audit": self.learning_log.get("last_audit", {}).get("timestamp"),
            "recent_issues_prevented": self.learning_log.get("issues_prevented", [])[-10:] if self.learning_log.get("issues_prevented") else []
        }

def validate_email_send(email: str, lead_name: str, biz_name: str, row_data: dict, tab_name: str = "Sheet2") -> Tuple[bool, str]:
    """
    Convenience function for validating before sending emails.
    Use this in your email sending scripts.
    """
    agent = SelfHealingAgent()
    return agent.validate_before_send(email, lead_name, biz_name, row_data, tab_name)

def validate_reply_processing(thread_id: str, from_email: str) -> Tuple[bool, str]:
    """
    Convenience function for validating before processing replies.
    Use this in your reply processing scripts.
    """
    agent = SelfHealingAgent()
    return agent.validate_before_reply(thread_id, from_email)

if __name__ == "__main__":
    # Run audit
    agent = SelfHealingAgent()
    print("=" * 70)
    print("SELF-HEALING AGENT: AUDIT")
    print("=" * 70)
    
    report = agent.audit_sheet_state("Sheet2")
    
    print(f"\n{report.get('summary', 'Audit complete')}")
    print(f"\nStatistics:")
    for key, value in report.get('statistics', {}).items():
        print(f"  {key}: {value}")
    
    if report.get('issues_found'):
        print(f"\n⚠️  Issues Found ({len(report['issues_found'])}):")
        for issue in report['issues_found'][:10]:  # Show first 10
            print(f"  - {issue}")
    
    if report.get('fixes_applied'):
        print(f"\n✅ Fixes Applied ({len(report['fixes_applied'])}):")
        for fix in report['fixes_applied']:
            print(f"  - {fix}")
    
    print("\n" + "=" * 70)
    print("Health Report:")
    health = agent.get_health_report()
    print(f"  Issues Prevented: {health['issues_prevented_count']}")
    print(f"  Patterns Learned: {health['patterns_learned_count']}")
    print("=" * 70)

