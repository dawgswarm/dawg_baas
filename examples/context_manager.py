"""Context manager - auto release on exit."""

from dawg_baas import Baas

API_KEY = "your_api_key"

with Baas(api_key=API_KEY) as ws_url:
    print(f"Got browser: {ws_url}")
    # Use with any framework...

print("Auto-released")
