#!/usr/bin/env python3
"""
Scrape table data from Wikipedia.

Usage:
    python cookbook/scrape_table.py
"""

from playwright.sync_api import sync_playwright
from dawg_baas import Baas

API_KEY = "your_api_key"
URL = "https://en.wikipedia.org/wiki/List_of_most-visited_websites"

with Baas(api_key=API_KEY) as ws_url:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        page.goto(URL, wait_until="networkidle")
        print(f"Loaded: {page.title()}\n")

        # Find table
        table = page.query_selector("table.wikitable")
        if not table:
            print("Table not found")
            browser.close()
            exit(1)

        # Extract rows
        rows = table.query_selector_all("tr")[1:11]  # First 10 data rows

        print("Top 10 Most Visited Websites:")
        print("-" * 30)

        for i, row in enumerate(rows, 1):
            cells = row.query_selector_all("td")
            if len(cells) >= 2:
                site = cells[0].inner_text().strip().split("[")[0]
                print(f"{i:2}. {site}")

        browser.close()

print("\nDone!")
