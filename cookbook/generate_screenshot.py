#!/usr/bin/env python3
"""
Take screenshots with different viewport sizes.

Usage:
    python cookbook/generate_screenshot.py
"""

from playwright.sync_api import sync_playwright
from dawg_baas import Baas

API_KEY = "your_api_key"
URL = "https://example.com"

VIEWPORTS = {
    "desktop": {"width": 1920, "height": 1080},
    "tablet": {"width": 768, "height": 1024},
    "mobile": {"width": 375, "height": 812},
}

with Baas(api_key=API_KEY) as ws_url:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        for device, viewport in VIEWPORTS.items():
            page.set_viewport_size(viewport)
            page.goto(URL, wait_until="networkidle")

            filename = f"screenshot_{device}.png"
            page.screenshot(path=filename)
            print(f"Saved: {filename} ({viewport['width']}x{viewport['height']})")

        browser.close()
