#!/usr/bin/env python3
"""
Fill and submit a web form.

Usage:
    python cookbook/fill_form.py
"""

from playwright.sync_api import sync_playwright
from dawg_baas import Baas
import time

API_KEY = "your_api_key"
URL = "https://httpbin.org/forms/post"

start_time=time.time()
with Baas(api_key=API_KEY) as ws_url:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        page.goto(URL, wait_until="networkidle")
        print("Form loaded")

        # Fill fields
        page.fill('input[name="custname"]', "John Doe")
        page.fill('input[name="custtel"]', "+1-555-123-4567")
        page.fill('input[name="custemail"]', "john.doe@example.com")
        print("Filled: name, phone, email")
        
        time.sleep(60)
        # Select options
        page.click('input[name="size"][value="medium"]')
        page.check('input[name="topping"][value="bacon"]')
        page.check('input[name="topping"][value="cheese"]')
        print("Selected: size, toppings")

        # More fields
        page.fill('input[name="delivery"]', "18:30")
        page.fill('textarea[name="comments"]', "Please ring the doorbell twice.")

        # Submit
        with page.expect_response(lambda r: "post" in r.url) as response_info:
            page.click('button:has-text("Submit order")')

        print(f"Response: {response_info.value.status}")

        browser.close()

print("Done!")
print("Time:", time.time()-start_time)
