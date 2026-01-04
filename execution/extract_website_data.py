#!/usr/bin/env python3
"""
Layer 3: Execution Script
Website Data Extractor
Visits websites to find contact emails and personalization hooks.
"""

import asyncio
import re
import sys
import json
from typing import List, Optional, Dict, Any
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# Simple regex for email detection
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

async def extract_website_data(url: str) -> Dict[str, Any]:
    """
    Visits a URL and its common contact pages to find email addresses 
    and website snippets for AI personalization.
    """
    if not url or not url.startswith('http'):
        return {"emails": [], "snippet": ""}

    emails = set()
    snippet = ""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Helper to scan a page
        async def scan_page(target_url, extract_snippet=False):
            nonlocal snippet
            try:
                print(f"Scanning: {target_url}")
                await page.goto(target_url, wait_until="domcontentloaded", timeout=10000)
                content = await page.content()
                
                # Regex search for emails
                found = re.findall(EMAIL_REGEX, content)
                for email in found:
                    if not any(ext in email.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', 'sentry.io']):
                        emails.add(email.lower())
                
                # Extract text snippet for AI (About page or homepage)
                if extract_snippet and not snippet:
                    # Remove script and style elements
                    soup = BeautifulSoup(content, 'html.parser')
                    for script_or_style in soup(["script", "style"]):
                        script_or_style.decompose()
                    
                    # Get text and clean it up
                    text = soup.get_text(separator=' ')
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    clean_text = ' '.join(lines)
                    snippet = clean_text[:3000] # Limit to 3000 chars for AI context
                    
            except Exception as e:
                print(f"Error scanning {target_url}: {e}")

        # Scan homepage and get initial snippet
        await scan_page(url, extract_snippet=True)
        
        # Try finding contact/about links
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
                        base = '/'.join(url.split('/')[:3])
                        contact_links.append(f"{base}{href}")
        except:
            pass

        # Scan found contact/about pages (limit to 2)
        for link in list(set(contact_links))[:2]:
            # If the link text or URL mentions "about" or "team", prefer its snippet over the homepage
            prefer_new_snippet = any(w in link.lower() for w in ['about', 'team', 'staff'])
            await scan_page(link, extract_snippet=prefer_new_snippet)

        await browser.close()
    
    return {
        "emails": list(emails),
        "snippet": snippet
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_website_data.py \"url\"")
        sys.exit(1)
    
    target_url = sys.argv[1]
    data = asyncio.run(extract_website_data(target_url))
    print(json.dumps(data, indent=2))
