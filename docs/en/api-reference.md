# API Reference

Reference for all SDK methods. If you're just getting started, check the "Quick Start" section first.

## Scraper Class

HTTP scraper — fast content extraction from pages without launching a browser.
Uses TLS fingerprinting to bypass anti-bot protections.

### Creating a Client

```python
from dawg_baas import Scraper

scraper = Scraper(api_key="your_key")
```

Parameters:
- `api_key` — your API key (required)
- `base_url` — service URL (default `https://dawgswarm.ru`)
- `timeout` — HTTP request timeout in seconds (default 60)

### Methods

#### `scrape(url, format="markdown", ...)`

Scrapes a single page and returns a `ScrapeResult`.

```python
result = scraper.scrape("https://example.com", format="markdown")
print(result.content)       # clean markdown
print(result.metadata)      # {"title": "...", "word_count": 42, ...}
```

Parameters:
- `url` — page URL
- `format` — output format: `"markdown"`, `"text"`, `"html"` (default `"markdown"`)
- `main_content` — strip navigation, footer, ads (default `False`)
- `include_links` — include list of found links (default `False`)
- `headers` — custom HTTP headers (dict)
- `timeout_ms` — page load timeout in ms (default 30000)
- `render` — rendering mode: `None` / `"auto"` (default, HTTP with automatic SPA fallback to browser), `"http"` (strict HTTP only, no browser fallback), or `"browser"` (force full browser rendering, billed at 0.5 min per request)

Returns `ScrapeResult`:
- `success` — whether it succeeded
- `content` — extracted content in the requested format
- `metadata` — `{"title", "description", "language", "word_count"}`
- `links` — list of links (if `include_links=True`)
- `final_url` — final URL after redirects
- `status_code` — target page HTTP status
- `elapsed_ms` — execution time

#### `crawl(url, max_depth=2, max_pages=50, ...)`

Recursive site crawl following links. Returns a `ScrapeJob` — a background task.

```python
job = scraper.crawl("https://example.com", max_depth=2, max_pages=20)
job.wait()  # wait for completion

for page in job.pages:
    print(page.url, page.metadata.get("title"))
```

Parameters:
- `url` — starting URL
- `format` — content format (default `"markdown"`)
- `max_depth` — crawl depth (default 2, max 5)
- `max_pages` — maximum pages (default 50, max 200)
- `concurrency` — parallel requests (default 3, max 10)
- `include_patterns` — URL glob patterns to include
- `exclude_patterns` — URL glob patterns to exclude
- `main_content` — strip boilerplate elements
- `timeout_ms` — timeout per page

#### `batch(urls, concurrency=5, ...)`

Parallel scraping of a URL list. Returns a `ScrapeJob`.

```python
job = scraper.batch([
    "https://example.com",
    "https://httpbin.org/html",
], format="text")
job.wait()

for page in job.pages:
    print(f"{page.url}: {len(page.content)} chars")
```

Parameters:
- `urls` — list of URLs (max 100)
- `format`, `concurrency`, `timeout_ms`, `main_content` — same as crawl

#### `get_job(job_id)` / `cancel_job(job_id)`

Get job status or cancel it.

### Working with Jobs (ScrapeJob)

`crawl()` and `batch()` return a `ScrapeJob`:

```python
job = scraper.crawl("https://example.com")

# Wait for completion (polling every 2 seconds)
job.wait(timeout=300, poll_interval=2.0)

# Or check status manually
job.refresh()
print(job.status)      # "running" | "completed" | "failed" | "cancelled"
print(job.progress)    # {"completed": 5, "total": 10, "errors": 0}

# Cancel
job.cancel()
```

### Recommended: with statement

```python
with Scraper(api_key="your_key") as s:
    result = s.scrape("https://example.com")
    print(result.content)
# HTTP session automatically closed
```

### Async Client: AsyncScraper

```python
from dawg_baas import AsyncScraper

async with AsyncScraper(api_key="your_key") as s:
    result = await s.scrape("https://example.com")

    job = await s.crawl("https://example.com", max_pages=10)
    await job.wait()
```

---

## Baas Class

Main class for working with the service. Lets you get a browser from the cloud
and connect to it via Playwright, Puppeteer, or any other CDP-compatible tool.

### Creating a Client

```python
from dawg_baas import Baas

baas = Baas(api_key="your_key")
```

Additional parameters (usually not needed):

- `timeout` — how long to wait for browser launch in seconds (default 60)
- `poll_interval` — how often to check browser readiness (default 2 sec)

### Methods

#### `create(proxy=None)`

Requests a browser from the pool and returns a connection URL.
This URL is passed to Playwright/Puppeteer to control the browser.

```python
# Get a connection URL for the browser
ws_url = baas.create()

# Or with a proxy (browser will access the internet through your proxy)
ws_url = baas.create(proxy="http://user:pass@proxy.com:8080")
```

#### `release()`

**Important to call after you're done!** Tells the service you've finished
using the browser. The browser is returned to the pool and can be assigned to another user.

If not called, the browser will be considered occupied until timeout (several minutes),
and you'll waste your limits.

```python
# Done working — release the browser
baas.release()
```

### Recommended: with statement

To avoid forgetting `release()`, use the `with` statement —
the browser is released automatically:

```python
from dawg_baas import Baas
from playwright.sync_api import sync_playwright

with Baas(api_key="your_key") as ws_url:
    # ws_url is the connection URL
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        page.goto("https://example.com")
        print(page.title())

        browser.close()

# Browser automatically released
```

> **Limitation of `with`:** when using `with`, you cannot pass a proxy.
> If you need a proxy, use `baas.create(proxy=...)` directly.

### Properties

- `baas.browser_id` — browser ID (for debugging)
- `baas.session_id` — session ID (for debugging)

---

## Async Client: AsyncBaas

If your code is async (using `async/await`),
use `AsyncBaas` — it works exactly the same way:

```python
from dawg_baas import AsyncBaas
from playwright.async_api import async_playwright

async def main():
    async with AsyncBaas(api_key="your_key") as ws_url:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(ws_url)
            page = browser.contexts[0].pages[0]

            await page.goto("https://example.com")
            print(await page.title())

            await browser.close()

# Run
import asyncio
asyncio.run(main())
```

---

## Error Handling

The SDK throws clear exceptions that you can handle:

### `AuthError`

Invalid API key. Check that the key was copied correctly.

### `RateLimitError`

Request limit for your plan exceeded.
The `retry_after` property shows how many seconds to wait before retrying.

### `BrowserNotReadyError`

The browser didn't start within the allotted time. Try again.

### `BaasError`

Base class for all errors. Catch this to handle any SDK error.

### Example

```python
from dawg_baas import Baas, AuthError, RateLimitError, BrowserNotReadyError
import time

baas = Baas(api_key="your_key")

try:
    ws_url = baas.create()
    # ... work with the browser ...

except AuthError:
    print("Error: invalid API key")

except RateLimitError as e:
    print(f"Limit exceeded. Wait {e.retry_after} seconds")
    time.sleep(e.retry_after)
    # Can retry the request

except BrowserNotReadyError:
    print("Browser didn't start, try again")

finally:
    baas.release()
```
