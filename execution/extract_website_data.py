#!/usr/bin/env python3
"""
Layer 3: Execution Script
The "Deep Data" Website Extractor
Uses Stealth Playwright for visual crawling and Markdown conversion for clean context.
Identifies "Golden Nuggets" and "Automation Gaps".
"""

import asyncio
import re
import sys
import json
from typing import List, Optional, Dict, Any
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# Simple regex for email detection
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

# Placeholder email patterns to filter out
PLACEHOLDER_DOMAINS = {
    "example.com", "domain.com", "mysite.com", "test.com", 
    "sample.com", "placeholder.com", "yourdomain.com", 
    "yoursite.com", "website.com", "email.com", "mail.com", "contact.com"
}

PLACEHOLDER_LOCAL_PARTS = {
    "johndoe", "janedoe", "user", "test", "sample", "demo", 
    "placeholder", "example", "admin", "info", "contact", 
    "support", "sales", "noreply", "no-reply", "donotreply"
}

def _is_placeholder_email(email: str) -> bool:
    """Check if email is a placeholder/fake email."""
    if '@' not in email:
        return True
    
    local_part, domain = email.split('@', 1)
    
    # Check placeholder domains
    if domain in PLACEHOLDER_DOMAINS:
        return True
    
    # Check placeholder local parts
    if local_part in PLACEHOLDER_LOCAL_PARTS:
        return True
    
    # Check generic patterns like "user@domain.com"
    if re.match(r'^(user|test|demo|sample|example|admin|info)@(domain|example|test|sample)\.com$', email):
        return True
    
    return False

async def extract_website_data(url: str) -> Dict[str, Any]:
    """
    Launches a local, stealth-enabled browser to visit key pages.
    Converts content to clean Markdown and identifies automation readiness.
    """
    if not url or not url.startswith('http'):
        return {"emails": [], "snippet": "", "social": {}, "automation_gaps": []}

    emails = set()
    social_links = {"linkedin": "", "facebook": "", "instagram": ""}
    markdown_context = []
    automation_gaps = []
    
    # Markers for automation/tech
    tech_markers = {
        "booking_widget": ["calendly", "acuity", "book-now", "appointment", "schedule-online", "housecallpro", "jobber"],
        "chat_widget": ["intercom", "drift", "zendesk", "livechat", "tidio", "chatbot"],
        "modern_form": ["typeform", "jotform", "wpforms", "gravity-forms"]
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        # Stealth removed temporarily due to import issues
        
        async def scan_page(target_url, page_type="General"):
            try:
                print(f"Deep Scanning ({page_type}): {target_url}")
                await page.goto(target_url, wait_until="domcontentloaded", timeout=15000)
                
                # Wait for lazy-loaded content
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)
                
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # 1. Extract Emails (with placeholder filtering)
                found_emails = re.findall(EMAIL_REGEX, content)
                for email in found_emails:
                    email_lower = email.lower()
                    # Filter out image files and known bad domains
                    if any(ext in email_lower for ext in ['.png', '.jpg', '.jpeg', '.gif', 'sentry.io', 'wixpress.com']):
                        continue
                    # Filter out obvious placeholders
                    if _is_placeholder_email(email_lower):
                        continue
                    emails.add(email_lower)

                # 2. Find Social Links
                links = await page.query_selector_all('a')
                for link in links:
                    href = await link.get_attribute('href')
                    if not href: continue
                    lower_href = href.lower()
                    if "linkedin.com/company" in lower_href or "linkedin.com/in" in lower_href:
                        social_links["linkedin"] = href
                    elif "facebook.com/" in lower_href and not any(x in lower_href for x in ["sharer", "messenger"]):
                        social_links["facebook"] = href
                    elif "instagram.com/" in lower_href:
                        social_links["instagram"] = href

                # 3. Check for Automation Gaps (Technical Audit)
                for tech, keywords in tech_markers.items():
                    if any(kw in content.lower() for kw in keywords):
                        if tech not in automation_gaps: automation_gaps.append(f"Found {tech}")
                
                # 4. Convert to Clean Markdown DNA
                # Remove noise
                for element in soup(["script", "style", "nav", "footer", "header"]):
                    element.decompose()
                
                page_md = md(str(soup), heading_style="ATX").strip()
                if page_md:
                    markdown_context.append(f"### PAGE: {page_type}\n{page_md[:2000]}") # Limit per page
                    
            except Exception as e:
                print(f"Error scanning {target_url}: {e}")

        # Phase 1: Homepage Audit
        await scan_page(url, "Homepage")
        
        # Phase 2: Find "Deep Data" Links (About, Team, Contact)
        target_pages = []
        try:
            links = await page.query_selector_all('a')
            for link in links:
                href = await link.get_attribute('href')
                text = (await link.inner_text()).lower()
                if href:
                    if any(word in href.lower() or word in text for word in ['about', 'team', 'staff', 'contact', 'history']):
                        full_url = href if href.startswith('http') else f"{url.rstrip('/')}/{href.lstrip('/')}"
                        if full_url not in [tp[0] for tp in target_pages] and full_url != url:
                            page_label = "About" if 'about' in text or 'history' in text else "Team" if 'team' in text or 'staff' in text else "Contact"
                            target_pages.append((full_url, page_label))
        except: pass

        # Scan up to 3 deep pages
        for deep_url, label in list(set(target_pages))[:3]:
            await scan_page(deep_url, label)

        await browser.close()
    
    # Final tech audit: What is MISSING?
    missing_tech = []
    if "Found booking_widget" not in automation_gaps: missing_tech.append("No Online Booking")
    if "Found chat_widget" not in automation_gaps: missing_tech.append("No Live Chat/AI Bot")
    
    return {
        "emails": list(emails),
        "social": social_links,
        "snippet": "\n\n".join(markdown_context),
        "automation_gaps": missing_tech
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_website_data.py \"url\"")
        sys.exit(1)
    
    target_url = sys.argv[1]
    data = asyncio.run(extract_website_data(target_url))
    print(json.dumps(data, indent=2))
