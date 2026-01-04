#!/usr/bin/env python3
"""
Layer 3: Execution Script
Email Verifier (The Shield)
Provides zero-cost email verification using MX record lookups and syntax validation.
"""

import re
import dns.resolver
from typing import Dict, Any

class EmailVerifier:
    def __init__(self):
        # Common disposable email domains to block
        self.disposable_domains = {
            "10minutemail.com", "guerrillamail.com", "temp-mail.org", 
            "mailinator.com", "dispostable.com", "getnada.com"
        }

    def verify(self, email: str) -> Dict[str, Any]:
        """
        Performs a multi-stage verification to ensure email deliverability.
        Returns a dict with 'valid' (bool) and 'reason' (str).
        """
        email = email.strip().lower()

        # 1. Syntax Check (Regex)
        regex = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
        if not re.match(regex, email):
            return {"valid": False, "reason": "Invalid syntax"}

        domain = email.split('@')[1]

        # 2. Disposable Domain Check
        if domain in self.disposable_domains:
            return {"valid": False, "reason": "Disposable email provider"}

        # 3. MX Record Check (The "Gold Standard" for free verification)
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
        "04isaacag@gmail.com", 
        "fake@nonexistentdomain12345.com", 
        "test@10minutemail.com", 
        "invalid-email"
    ]
    
    print("--- STARTING EMAIL VERIFICATION TEST ---")
    for email in test_emails:
        result = verifier.verify(email)
        status = "PASS" if result['valid'] else "FAIL"
        print(f"[{status}] {email} -> {result['reason']}")

