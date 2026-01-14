"""Example with Playwright."""

from playwright.sync_api import sync_playwright
from dawg_baas import Baas

API_KEY = "your_api_key"

with Baas(api_key=API_KEY) as ws_url:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        page.goto("https://example.com")
        print(f"Title: {page.title()}")
        page.screenshot(path="screenshot.png")

        browser.close()
