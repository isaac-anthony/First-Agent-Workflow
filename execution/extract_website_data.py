#!/usr/bin/env python3
"""
Layer 3: Execution Script
Website Data Extractor
Visits websites to find contact emails and other lead details.
"""

import asyncio
import re
import sys
import json
from typing import List, Optional
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# Simple regex for email detection
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

async def extract_emails_from_url(url: str) -> List[str]:
    """
    Visits a URL and its common contact pages to find email addresses.
    """
    if not url or not url.startswith('http'):
        return []

    emails = set()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Helper to scan a page
        async def scan_page(target_url):
            try:
                print(f"Scanning: {target_url}")
                await page.goto(target_url, wait_until="domcontentloaded", timeout=10000)
                content = await page.content()
                
                # Regex search
                found = re.findall(EMAIL_REGEX, content)
                for email in found:
                    # Filter out common junk
                    if not any(ext in email.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', 'sentry.io']):
                        emails.add(email.lower())
            except Exception as e:
                print(f"Error scanning {target_url}: {e}")

        # Scan homepage
        await scan_page(url)
        
        # Try finding contact links
        contact_links = []
        try:
            links = await page.query_selector_all('a')
            for link in links:
                href = await link.get_attribute('href')
                text = await link.inner_text()
                if href and any(word in href.lower() or word in text.lower() for word in ['contact', 'about', 'team']):
                    if href.startswith('http'):
                        contact_links.append(href)
                    elif href.startswith('/'):
                        # Join with base URL
                        base = '/'.join(url.split('/')[:3])
                        contact_links.append(f"{base}{href}")
        except:
            pass

        # Scan found contact pages (limit to 2)
        for link in list(set(contact_links))[:2]:
            if len(emails) >= 3: break # Enough emails
            await scan_page(link)

        await browser.close()
    
    return list(emails)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_website_data.py \"url\"")
        sys.exit(1)
    
    target_url = sys.argv[1]
    found_emails = asyncio.run(extract_emails_from_url(target_url))
    print(json.dumps(found_emails))

