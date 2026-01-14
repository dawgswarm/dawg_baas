# Cookbook

Real-world examples using dawg-baas SDK.

## Setup

```bash
pip install dawg-baas playwright
playwright install chromium
```

## Examples

| File | Description |
|------|-------------|
| `fill_form.py` | Fill and submit web forms |
| `generate_pdf.py` | Generate PDF from webpage |
| `generate_screenshot.py` | Screenshots with different viewports |
| `scrape_table.py` | Scrape table data from Wikipedia |
| `spa_scrape.py` | Scrape JavaScript-rendered content |

## Usage

1. Set your API key in the script:
   ```python
   API_KEY = "your_api_key"
   ```

2. Run:
   ```bash
   python cookbook/fill_form.py
   ```

## Pattern

All examples follow the same pattern:

```python
from playwright.sync_api import sync_playwright
from dawg_baas import Baas

API_KEY = "your_api_key"

with Baas(api_key=API_KEY) as ws_url:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = browser.contexts[0].pages[0]

        # Your automation code
        page.goto("https://example.com")
        print(page.title())

        browser.close()
```

## With Proxy

```python
from dawg_baas import Baas

baas = Baas(api_key=API_KEY)
ws_url = baas.create(proxy="socks5://user:pass@host:port")
# ...
baas.release()
```
