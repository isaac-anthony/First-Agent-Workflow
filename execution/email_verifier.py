#!/usr/bin/env python3
"""
Layer 3: Execution Script
Email Verifier (The Shield)
Provides zero-cost email verification using MX record lookups and syntax validation.
Enhanced with placeholder email detection and self-healing learning.
"""

import re
import os
import json
import dns.resolver
from typing import Dict, Any, List
from datetime import datetime

class EmailVerifier:
    def __init__(self):
        # Common disposable email domains to block
        self.disposable_domains = {
            "10minutemail.com", "guerrillamail.com", "temp-mail.org", 
            "mailinator.com", "dispostable.com", "getnada.com"
        }
        
        # Load fake email patterns knowledge base
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.patterns_path = os.path.join(project_root, "knowledge_base", "fake_email_patterns.json")
        self._load_patterns()
    
    def _load_patterns(self):
        """Load fake email patterns from knowledge base."""
        if os.path.exists(self.patterns_path):
            try:
                with open(self.patterns_path, 'r') as f:
                    data = json.load(f)
                    self.placeholder_domains = set(data.get("placeholder_domains", []))
                    self.placeholder_local_parts = set(data.get("placeholder_local_parts", []))
                    self.suspicious_patterns = data.get("suspicious_patterns", [])
                    self.learned_fake_emails = set(data.get("learned_fake_emails", []))
                    self.failed_emails = data.get("failed_emails", [])
            except Exception as e:
                print(f"Warning: Could not load email patterns: {e}")
                self._init_default_patterns()
        else:
            self._init_default_patterns()
    
    def _init_default_patterns(self):
        """Initialize default patterns if knowledge base doesn't exist."""
        self.placeholder_domains = {
            "example.com", "domain.com", "mysite.com", "test.com", 
            "sample.com", "placeholder.com", "yourdomain.com", 
            "yoursite.com", "website.com", "email.com", "mail.com", "contact.com"
        }
        self.placeholder_local_parts = {
            "johndoe", "janedoe", "user", "test", "sample", "demo", 
            "placeholder", "example"
            # Note: "admin", "info", "contact", "support", "sales" are legitimate business emails
            # Only flag them if combined with placeholder domains
        }
        self.suspicious_patterns = [
            {
                "pattern": "^[a-z]+@[a-z]+\\.com$",
                "description": "Generic pattern like 'user@domain.com'",
                "confidence": 0.7
            },
            {
                "pattern": "^(test|demo|sample|example)@",
                "description": "Test/demo email addresses",
                "confidence": 0.9
            },
            {
                "pattern": "@(example|domain|mysite|test|sample)\\.com$",
                "description": "Known placeholder domains",
                "confidence": 1.0
            }
        ]
        self.learned_fake_emails = set()
        self.failed_emails = []
    
    def _save_patterns(self):
        """Save patterns to knowledge base."""
        os.makedirs(os.path.dirname(self.patterns_path), exist_ok=True)
        data = {
            "placeholder_domains": list(self.placeholder_domains),
            "placeholder_local_parts": list(self.placeholder_local_parts),
            "suspicious_patterns": self.suspicious_patterns,
            "learned_fake_emails": list(self.learned_fake_emails),
            "failed_emails": self.failed_emails[-100:],  # Keep last 100
            "last_updated": datetime.now().isoformat()
        }
        with open(self.patterns_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def learn_from_failure(self, email: str, reason: str):
        """
        Self-healing: Learn from failed email sends.
        Updates knowledge base to prevent future failures.
        """
        email = email.strip().lower()
        
        # Add to failed emails log
        self.failed_emails.append({
            "email": email,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        
        # Extract domain and local part
        if '@' in email:
            local_part, domain = email.split('@', 1)
            
            # If it's a placeholder domain, add it
            if domain in ["example.com", "domain.com", "mysite.com", "test.com", "sample.com"]:
                self.placeholder_domains.add(domain)
            
            # If local part is generic, add it
            if local_part in ["johndoe", "janedoe", "user", "test", "sample", "demo", "example"]:
                self.placeholder_local_parts.add(local_part)
            
            # Add full email to learned fake emails
            self.learned_fake_emails.add(email)
        
        # Save updated patterns
        self._save_patterns()
    
    def verify(self, email: str) -> Dict[str, Any]:
        """
        Performs a multi-stage verification to ensure email deliverability.
        Returns a dict with 'valid' (bool) and 'reason' (str).
        """
        email = email.strip().lower()

        # 0. Check learned fake emails (highest priority)
        if email in self.learned_fake_emails:
            return {"valid": False, "reason": "Known fake/placeholder email (learned)"}

        # 1. Syntax Check (Regex)
        regex = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
        if not re.match(regex, email):
            return {"valid": False, "reason": "Invalid syntax"}

        if '@' not in email:
            return {"valid": False, "reason": "Missing @ symbol"}

        local_part, domain = email.split('@', 1)

        # 2. Placeholder Domain Check
        if domain in self.placeholder_domains:
            return {"valid": False, "reason": f"Placeholder domain: {domain}"}

        # 3. Placeholder Local Part Check (only for obvious placeholders)
        # Only flag if it's a placeholder local part AND a placeholder domain
        if local_part in self.placeholder_local_parts and domain in self.placeholder_domains:
            return {"valid": False, "reason": f"Placeholder email pattern: {local_part}@{domain}"}

        # 4. Suspicious Pattern Check
        for pattern_info in self.suspicious_patterns:
            pattern = pattern_info["pattern"]
            if re.match(pattern, email):
                confidence = pattern_info.get("confidence", 0.5)
                if confidence >= 0.8:  # High confidence patterns
                    return {"valid": False, "reason": f"Suspicious pattern: {pattern_info['description']}"}

        # 5. Disposable Domain Check
        if domain in self.disposable_domains:
            return {"valid": False, "reason": "Disposable email provider"}

        # 6. MX Record Check (The "Gold Standard" for free verification)
        try:
            # Check if the domain has a Mail Exchange record
            records = dns.resolver.resolve(domain, 'MX')
            if not records:
                return {"valid": False, "reason": "No MX records found for domain"}
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout):
            return {"valid": False, "reason": "Domain does not exist or has no mail server"}
        except Exception as e:
            return {"valid": False, "reason": f"DNS Lookup failed: {str(e)}"}

        return {"valid": True, "reason": "Verified (MX Record Found)"}

if __name__ == "__main__":
    # Test cases
    verifier = EmailVerifier()
    test_emails = [
        "brineaiconsulting@gmail.com", 
        "fake@nonexistentdomain12345.com", 
        "test@10minutemail.com", 
        "invalid-email"
    ]
    
    print("--- STARTING EMAIL VERIFICATION TEST ---")
    for email in test_emails:
        result = verifier.verify(email)
        status = "PASS" if result['valid'] else "FAIL"
        print(f"[{status}] {email} -> {result['reason']}")


