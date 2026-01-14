#!/usr/bin/env python3
"""
Generate PDF from a webpage using CDP.

Usage:
    python cookbook/generate_pdf.py
"""

import base64
from playwright.sync_api import sync_playwright
from dawg_baas import Baas

API_KEY = "your_api_key"
URL = "https://example.com"
OUTPUT = "output.pdf"

with Baas(api_key=API_KEY) as ws_url:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        page.goto(URL, wait_until="networkidle")
        print(f"Loaded: {page.title()}")

        # Use CDP for PDF generation
        cdp = page.context.new_cdp_session(page)
        result = cdp.send("Page.printToPDF", {
            "printBackground": True,
            "preferCSSPageSize": True,
        })

        # Save PDF
        pdf_data = base64.b64decode(result["data"])
        with open(OUTPUT, "wb") as f:
            f.write(pdf_data)

        print(f"Saved: {OUTPUT} ({len(pdf_data) / 1024:.1f} KB)")

        browser.close()
