# dawg-baas

Minimal Python SDK for BaaS (Browser as a Service).

Get browser access via CDP WebSocket URL. Use with any automation framework.

## Installation

```bash
pip install dawg-baas
```

## Usage

```python
from dawg_baas import Baas

# Create browser, get ws_url
baas = Baas(api_key="your_key")
ws_url = baas.create()

# Use with your framework (Playwright, Puppeteer, Selenium, etc.)
browser = playwright.chromium.connect_over_cdp(ws_url)
# ... your code ...

# Release when done
baas.release()
```

### Context Manager

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
    # ...
```

Or manually:

```python
baas = AsyncBaas(api_key="your_key")
ws_url = await baas.create()
# ...
await baas.release()
```

## API

### `Baas(api_key, base_url=None, timeout=60, poll_interval=2)`

- `api_key` - Your API key (required)
- `base_url` - Service URL (default: `http://37.195.230.102:8000`)
- `timeout` - Max seconds to wait for browser (default: 60)
- `poll_interval` - Seconds between ready checks (default: 2)

#### Methods

- `create(proxy=None) -> str` - Create browser, returns `ws_url`
- `release()` - Release browser back to pool
- `close()` - Close HTTP session

#### Properties

- `browser_id` - Current browser ID
- `session_id` - Current session ID

### `AsyncBaas`

Same as `Baas`, but async.

## Exceptions

```python
from dawg_baas import BaasError, AuthError, RateLimitError, BrowserNotReadyError

try:
    with Baas(api_key="bad_key") as ws_url:
        pass
except AuthError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limit, retry after {e.retry_after}s")
except BrowserNotReadyError:
    print("Browser didn't start in time")
```

## Examples

### Playwright

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

### Selenium (with CDP)

```python
from selenium import webdriver
from dawg_baas import Baas

with Baas(api_key="your_key") as ws_url:
    options = webdriver.ChromeOptions()
    options.debugger_address = ws_url.replace("ws://", "").split("/")[0]
    driver = webdriver.Chrome(options=options)
    driver.get("https://example.com")
    print(driver.title)
    driver.quit()
```

## License

MIT
