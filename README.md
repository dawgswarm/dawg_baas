# dawg-baas

Python SDK for BaaS (Browser as a Service).

Two tools in one SDK:
- **Baas** — cloud browser via CDP WebSocket (Playwright, Puppeteer, Selenium)
- **Scraper** — fast HTTP scraping with content extraction (no browser needed)

## Installation

```bash
pip install dawg-baas
```

## Scraper — HTTP scraping

Extract clean content from web pages without a browser. Fast, cheap, TLS-fingerprinted.

```python
from dawg_baas import Scraper

with Scraper(api_key="your_key") as s:
    # Single page → markdown
    result = s.scrape("https://example.com")
    print(result.content)

    # Crawl a site
    job = s.crawl("https://example.com", max_depth=2, max_pages=20)
    job.wait()
    for page in job.pages:
        print(page.url, len(page.content))

    # Batch scrape
    job = s.batch(["https://a.com", "https://b.com"])
    job.wait()
```

### Scraper Methods

- `scrape(url, format="markdown", main_content=False, include_links=False)` → `ScrapeResult`
- `crawl(url, max_depth=2, max_pages=50, concurrency=3)` → `ScrapeJob`
- `batch(urls, concurrency=5)` → `ScrapeJob`
- `get_job(job_id)` → `ScrapeJob`
- `cancel_job(job_id)`

Formats: `"markdown"`, `"text"`, `"html"`

Jobs (crawl/batch) are async — use `job.wait()` to block until done, or `job.refresh()` to poll manually.

## Browser — CDP access

Get a cloud browser via WebSocket. Use with any automation framework.

```python
from dawg_baas import Baas

with Baas(api_key="your_key") as ws_url:
    browser = playwright.chromium.connect_over_cdp(ws_url)
    # ... your code ...
# auto-released
```

### With Proxy

```python
baas = Baas(api_key="your_key")
ws_url = baas.create(proxy="socks5://user:pass@host:port")
```

### Async

```python
from dawg_baas import AsyncBaas

async with AsyncBaas(api_key="your_key") as ws_url:
    browser = await playwright.chromium.connect_over_cdp(ws_url)
```

### Browser Methods

- `create(proxy=None, geo=None) -> str` — returns `ws_url`
- `release()` — release browser back to pool
- `close()` — close HTTP session

## Exceptions

```python
from dawg_baas import BaasError, AuthError, RateLimitError

try:
    result = scraper.scrape("https://example.com")
except AuthError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limit, retry after {e.retry_after}s")
```

## Examples

### Scrape to markdown

```python
from dawg_baas import Scraper

s = Scraper(api_key="your_key")
result = s.scrape("https://news.ycombinator.com", format="markdown", main_content=True)
print(result.metadata["title"])
print(result.content)
s.close()
```

### Playwright browser

```python
from playwright.sync_api import sync_playwright
from dawg_baas import Baas

with Baas(api_key="your_key") as ws_url:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]
        page.goto("https://example.com")
        print(page.title())
        browser.close()
```

## License

MIT
