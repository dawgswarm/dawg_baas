"""Example with proxy."""

from dawg_baas import Baas

API_KEY = "your_api_key"
PROXY = "socks5://user:pass@proxy.example.com:1080"

baas = Baas(api_key=API_KEY)
ws_url = baas.create(proxy=PROXY)

print(f"Browser with proxy: {ws_url}")

# Use with any framework...

baas.release()
