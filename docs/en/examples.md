# Examples

Basic SDK usage examples for various scenarios.

## Sync Client

Simple example without a context manager:

```python
from dawg_baas import Baas

baas = Baas(api_key="your_api_key")

try:
    # Create a browser
    ws_url = baas.create()
    print(f"Browser ready: {ws_url}")

    # Your browser code here
    # ...

finally:
    # Always return the browser to the pool
    baas.release()
```

## Async Client

```python
import asyncio
from dawg_baas import AsyncBaas

async def main():
    baas = AsyncBaas(api_key="your_api_key")

    try:
        ws_url = await baas.create()
        print(f"Browser ready: {ws_url}")

        # Your async code here
        # ...

    finally:
        # Always return the browser to the pool
        await baas.release()

asyncio.run(main())
```

## With Context Manager

Recommended approach — browser is automatically released:

```python
from dawg_baas import Baas

with Baas(api_key="your_api_key") as ws_url:
    print(f"Browser ready: {ws_url}")
    # Work with the browser
    # ...

# Browser automatically returned to the pool
```

## With Proxy

SOCKS5 and HTTP proxies are supported. When using a proxy, manage
the browser manually (context manager `with` does not support proxy):

```python
from dawg_baas import Baas

# Formats: socks5://user:pass@host:port or http://user:pass@host:port
PROXY = "http://user:pass@proxy.example.com:8080"

baas = Baas(api_key="your_api_key")

try:
    ws_url = baas.create(proxy=PROXY)
    # Work with the browser...
finally:
    baas.release()
```

## With Playwright

```python
from dawg_baas import Baas
from playwright.sync_api import sync_playwright

with Baas(api_key="your_api_key") as ws_url:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        page.goto("https://example.com")
        print(page.title())

        browser.close()
```

## Error Handling

```python
from dawg_baas import (
    Baas,
    BaasError,
    AuthError,
    RateLimitError,
    BrowserNotReadyError
)
import time

def run_with_retry(api_key: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            with Baas(api_key=api_key) as ws_url:
                print(f"Connected: {ws_url}")
                # Your code here
                return True

        except AuthError:
            print("Error: invalid API key")
            return False

        except RateLimitError as e:
            print(f"Rate limit exceeded. Waiting {e.retry_after} sec...")
            time.sleep(e.retry_after)

        except BrowserNotReadyError:
            print(f"Attempt {attempt + 1}: browser not ready")
            time.sleep(5)

        except BaasError as e:
            print(f"Error: {e.message}")
            return False

    return False

run_with_retry("your_api_key")
```

## Parallel Browsers

```python
import asyncio
from dawg_baas import AsyncBaas

async def process_url(api_key: str, url: str):
    async with AsyncBaas(api_key=api_key) as ws_url:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(ws_url)
            page = browser.contexts[0].pages[0]
            await page.goto(url)
            title = await page.title()
            await browser.close()
            return title

async def main():
    api_key = "your_api_key"
    urls = [
        "https://example.com",
        "https://httpbin.org",
        "https://jsonplaceholder.typicode.com"
    ]

    # Run in parallel
    tasks = [process_url(api_key, url) for url in urls]
    results = await asyncio.gather(*tasks)

    for url, title in zip(urls, results):
        print(f"{url}: {title}")

asyncio.run(main())
```
