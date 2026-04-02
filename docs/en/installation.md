# Installation

dawg-baas is a Python SDK for DAWG Browser-as-a-Service.
It lets you manage remote browsers through a simple API.

## Requirements

- Python 3.9 or higher
- pip (Python package manager)

## Install via pip

```bash
pip install dawg-baas
```

## Dependencies

The SDK automatically installs the following dependencies:

- `httpx` — for async HTTP requests
- `requests` — for sync HTTP requests

## Optional Libraries

To work with the browser, install one of the automation libraries:

```bash
# Playwright (recommended)
pip install playwright
playwright install chromium

# Or Selenium
pip install selenium
```

## Verify Installation

```python
from dawg_baas import Baas

print("dawg-baas installed successfully!")
```
