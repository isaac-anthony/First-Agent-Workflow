#!/usr/bin/env python3
"""
Layer 3: Execution Script
Google Maps Scraper using Playwright
Extracts business details for small business lead generation.
"""

import asyncio
import json
import os
import sys
from typing import List, Dict, Any
from playwright.async_api import async_playwright
# Remove stealth for now to ensure baseline functionality
# from playwright_stealth import stealth_async as stealth 

async def scrape_google_maps(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Scrapes Google Maps for business listings based on a query.
    """
    results = []
    
    async with async_playwright() as p:
        # Launch browser in headless mode
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        # Stealth is optional for Google Maps if using high-quality UA
        
        # Go to Google Maps
        print(f"Searching Google Maps for: {query}")
        await page.goto(f"https://www.google.com/maps/search/{query.replace(' ', '+')}")
        
        # Wait for results to load
        try:
            await page.wait_for_selector('div[role="feed"]', timeout=10000)
        except:
            print("Timeout waiting for results feed. Check if the query returned results.")
            await browser.close()
            return []

        # Scrape loop
        while len(results) < limit:
            # Find all business listing cards
            # The selector for the cards often changes, but 'div[role="article"]' or specific class patterns work
            listings = await page.query_selector_all('div[role="article"]')
            
            for listing in listings:
                if len(results) >= limit:
                    break
                
                try:
                    # Basic Extraction
                    name = await listing.get_attribute('aria-label')
                    
                    # Click to get details (opens sidebar)
                    await listing.click()
                    await page.wait_for_timeout(2000) # Wait for sidebar
                    
                    # Extract details from sidebar
                    website = ""
                    phone = ""
                    address = ""
                    reviews_count = 0
                    rating = 0.0
                    
                    # Extract Rating and Review Count
                    # Improved selector for rating/reviews
                    rating_el = await page.query_selector('span[role="img"][aria-label*="stars"]')
                    if rating_el:
                        rating_text = await rating_el.get_attribute('aria-label')
                        if rating_text:
                            try:
                                # Extract rating (usually the first number)
                                import re
                                rating_match = re.search(r"(\d+\.?\d*)", rating_text)
                                if rating_match:
                                    rating = float(rating_match.group(1))
                                
                                # Try to find the reviews count
                                # Search for the button with aria-label containing 'reviews' or just the text
                                reviews_el = await page.query_selector('button[aria-label*="reviews"]')
                                if not reviews_el:
                                    # Fallback: look for a span or button containing the word 'reviews'
                                    reviews_el = await page.query_selector('span[aria-label*="reviews"]')
                                
                                if reviews_el:
                                    reviews_text = await reviews_el.get_attribute('aria-label')
                                    # Handle both "123 reviews" and "1,234 reviews"
                                    # We look for the number immediately followed by space and 'reviews' or just the number in the label
                                    import re
                                    reviews_match = re.search(r"(\d+[,.]?\d*)\s*reviews", reviews_text.lower())
                                    if not reviews_match:
                                        # Alternative: just find the first number in the button/span label
                                        reviews_match = re.search(r"(\d+[,.]?\d*)", reviews_text)
                                    
                                    if reviews_match:
                                        reviews_count = int(reviews_match.group(1).replace(',', '').replace('.', ''))
                                    
                                # Final fallback: try to find any text in the sidebar that matches the pattern
                                if reviews_count == 0:
                                    sidebar = await page.query_selector('div[role="main"]')
                                    if sidebar:
                                        sidebar_text = await sidebar.inner_text()
                                        match = re.search(r"(\d+[,.]?\d*)\s*reviews", sidebar_text.lower())
                                        if match:
                                            reviews_count = int(match.group(1).replace(',', '').replace('.', ''))
                            except Exception as e:
                                print(f"Error parsing reviews: {e}")
                                pass

                    # Look for website link
                    website_el = await page.query_selector('a[data-item-id="authority"]')
                    if website_el:
                        website = await website_el.get_attribute('href')
                    
                    # Look for phone
                    phone_el = await page.query_selector('button[data-item-id^="phone:tel:"]')
                    if phone_el:
                        phone = await phone_el.get_attribute('data-item-id')
                        phone = phone.replace('phone:tel:', '')

                    # Look for address
                    address_el = await page.query_selector('button[data-item-id="address"]')
                    if address_el:
                        address = await address_el.get_attribute('aria-label')
                        address = address.replace('Address: ', '')

                    result = {
                        "name": name,
                        "website": website,
                        "phone": phone,
                        "address": address,
                        "reviews_count": reviews_count,
                        "rating": rating,
                        "query": query
                    }
                    
                    # Deduplicate in the current run
                    if not any(r['name'] == name for r in results):
                        results.append(result)
                        print(f"Found: {name} | Website: {website or 'N/A'}")
                
                except Exception as e:
                    continue

            # Scroll down to load more
            await page.mouse.wheel(0, 2000)
            await page.wait_for_timeout(2000)
            
            # Check if we've reached the end
            end_msg = await page.query_selector('text="You\'ve reached the end of the list."')
            if end_msg:
                break

        await browser.close()
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scrape_google_maps.py \"search query\" [limit]")
        sys.exit(1)
    
    search_query = sys.argv[1]
    search_limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    leads = asyncio.run(scrape_google_maps(search_query, search_limit))
    print(json.dumps(leads, indent=2))

