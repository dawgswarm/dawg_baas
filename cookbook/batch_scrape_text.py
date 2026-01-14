#!/usr/bin/env python3
"""
Batch scrape text content from multiple URLs and save to individual files.

Usage:
    python cookbook/batch_scrape_text.py
"""

from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright
from dawg_baas import Baas

API_KEY = "your_api_key"
OUTPUT_DIR = Path("texts")

URLS = [
    "https://dawgswarm.ru/privacy",
    "https://dawgswarm.ru/terms",
    "https://dawgswarm.ru/offer",
    "https://dawgswarm.ru/cookies",
]


def url_to_filename(url: str) -> str:
    """Convert URL to a filename."""
    parsed = urlparse(url)
    # Use path as filename, replace / with _
    path = parsed.path.strip("/").replace("/", "_") or "index"
    return f"{path}.txt"


def extract_text(page) -> str:
    """Extract readable text content from page."""
    # Remove script and style elements, then get text
    return page.evaluate("""() => {
        // Remove scripts, styles, and hidden elements
        const elementsToRemove = document.querySelectorAll('script, style, noscript, iframe');
        elementsToRemove.forEach(el => el.remove());

        // Get the main content area or body
        const main = document.querySelector('main, article, .content, #content') || document.body;

        // Get text and clean it up
        return main.innerText
            .split('\\n')
            .map(line => line.trim())
            .filter(line => line.length > 0)
            .join('\\n');
    }""")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    with Baas(api_key=API_KEY) as ws_url:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(ws_url)
            page = browser.contexts[0].pages[0]

            for url in URLS:
                print(f"Scraping: {url}")

                page.goto(url, wait_until="networkidle")

                # Wait for content to load
                page.wait_for_load_state("domcontentloaded")

                # Extract text
                text_content = extract_text(page)

                # Save to file
                filename = url_to_filename(url)
                output_path = OUTPUT_DIR / filename

                output_path.write_text(text_content, encoding="utf-8")
                print(f"  -> Saved: {output_path} ({len(text_content)} chars)")

            browser.close()

    print(f"\nDone! Saved {len(URLS)} files to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
