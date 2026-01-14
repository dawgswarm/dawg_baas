"""Async example."""

import asyncio
from dawg_baas import AsyncBaas

API_KEY = "your_api_key"


async def main():
    async with AsyncBaas(api_key=API_KEY) as ws_url:
        print(f"Got browser: {ws_url}")
        # Use with async playwright, etc.


asyncio.run(main())
