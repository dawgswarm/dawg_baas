#!/usr/bin/env python3
"""
Scrape JavaScript-rendered SPA content.

Usage:
    python cookbook/spa_scrape.py
"""

from playwright.sync_api import sync_playwright
from dawg_baas import Baas

API_KEY = "your_api_key"
URL = "https://quotes.toscrape.com/js/"

with Baas(api_key=API_KEY) as ws_url:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        page.goto(URL)
        print("Page loaded (waiting for JS render...)")

        # Wait for dynamic content
        page.wait_for_selector(".quote", timeout=10000)
        print("Content rendered!\n")

        # Extract data via JavaScript (faster than multiple DOM queries)
        quotes = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('.quote')).map(q => ({
                text: q.querySelector('.text')?.innerText || '',
                author: q.querySelector('.author')?.innerText || '',
                tags: Array.from(q.querySelectorAll('.tag')).map(t => t.innerText)
            }));
        }""")

        print(f"Found {len(quotes)} quotes:\n")
        for i, q in enumerate(quotes[:5], 1):
            print(f"{i}. {q['text'][:50]}...")
            print(f"   - {q['author']}")
            print(f"   Tags: {', '.join(q['tags'])}\n")

        # Navigate to page 2
        next_btn = page.query_selector("li.next a")
        if next_btn:
            next_btn.click()
            page.wait_for_selector(".quote")
            count = page.evaluate("document.querySelectorAll('.quote').length")
            print(f"Page 2: {count} quotes")

        browser.close()

print("Done!")
