# Quick Start

Get started with DAWG BaaS in minutes. Get an API key from the dashboard
and use the examples below.

## Getting an API Key

1. Register on the website
2. Go to the "API Keys" section in the dashboard
3. Create a new key

## Minimal Example

The simplest way is to use a context manager:

```python
from dawg_baas import Baas

# Context manager automatically releases the browser
with Baas(api_key="your_api_key") as ws_url:
    print(f"WebSocket URL: {ws_url}")
    # Connect to the browser via ws_url
```

## Playwright Example

Integration with Playwright for browser automation:

```python
from dawg_baas import Baas
from playwright.sync_api import sync_playwright

API_KEY = "your_api_key"

with Baas(api_key=API_KEY) as ws_url:
    with sync_playwright() as p:
        # Connect to the remote browser
        browser = p.chromium.connect_over_cdp(ws_url)

        # Get the page
        page = browser.contexts[0].pages[0]

        # Work with the browser
        page.goto("https://example.com")
        print(f"Title: {page.title()}")

        # Take a screenshot
        page.screenshot(path="screenshot.png")

        browser.close()

print("Done!")
```

## Async Example

For async code, use `AsyncBaas`:

```python
import asyncio
from dawg_baas import AsyncBaas
from playwright.async_api import async_playwright

async def main():
    async with AsyncBaas(api_key="your_api_key") as ws_url:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(ws_url)
            page = browser.contexts[0].pages[0]

            await page.goto("https://example.com")
            print(f"Title: {await page.title()}")

            await browser.close()

asyncio.run(main())
```

> **Important:** The browser is automatically returned to the pool when exiting
> the context manager. This allows efficient resource reuse.
