#!/usr/bin/env python3
"""
Batch PDF generation - save multiple pages as individual PDF files.

Usage:
    python cookbook/batch_pdf.py
"""

import base64
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright
from dawg_baas import Baas

API_KEY = "your_api_key"
OUTPUT_DIR = Path("pdfs")

URLS = [
    "https://example1-to-pdf.ru",
    "https://example2-to-pdf.ru",
    "https://example3-to-pdf.ru"
]


def url_to_filename(url: str) -> str:
    """Convert URL to a safe filename."""
    path = urlparse(url).path.strip("/")
    return f"{path or 'index'}.pdf"


def save_page_as_pdf(page, cdp, url: str, output_path: Path) -> None:
    """Navigate to URL and save as PDF."""
    page.goto(url, wait_until="networkidle")
    print(f"Loaded: {page.title()} ({url})")

    result = cdp.send("Page.printToPDF", {
        "printBackground": True,
        "preferCSSPageSize": True,
    })

    pdf_data = base64.b64decode(result["data"])
    output_path.write_bytes(pdf_data)
    print(f"Saved: {output_path} ({len(pdf_data) / 1024:.1f} KB)")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    with Baas(api_key=API_KEY) as ws_url:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(ws_url)
            page = browser.contexts[0].pages[0]
            cdp = page.context.new_cdp_session(page)

            for url in URLS:
                filename = url_to_filename(url)
                output_path = OUTPUT_DIR / filename
                save_page_as_pdf(page, cdp, url, output_path)

            browser.close()

    print(f"\nDone! {len(URLS)} PDFs saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
