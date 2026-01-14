"""Simple example - get browser, use it, release."""

from dawg_baas import Baas

API_KEY = "your_api_key"

# Get browser
baas = Baas(api_key=API_KEY)
ws_url = baas.create()

print(f"Got browser: {ws_url}")

# Use with any framework...
# browser = playwright.chromium.connect_over_cdp(ws_url)

# Release
baas.release()
print("Released")
