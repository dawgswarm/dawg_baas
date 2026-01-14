"""
dawg-baas - Python SDK for BaaS (Browser as a Service)

Simple SDK to get browser access. Use ws_url with any CDP client.

Usage:
    from dawg_baas import Baas

    # Simple
    baas = Baas(api_key="your_key")
    ws_url = baas.create()
    # ... your automation code with any framework ...
    baas.release()

    # Context manager (auto-release)
    with Baas(api_key="your_key") as ws_url:
        # ... your code ...

    # With proxy
    baas = Baas(api_key="your_key")
    ws_url = baas.create(proxy="socks5://user:pass@host:port")

    # Async
    baas = AsyncBaas(api_key="your_key")
    ws_url = await baas.create()
    await baas.release()
"""

from .version import __version__
from .client import Baas, AsyncBaas
from .exceptions import (
    BaasError,
    AuthError,
    RateLimitError,
    BrowserNotReadyError,
)

__all__ = [
    "__version__",
    "Baas",
    "AsyncBaas",
    "BaasError",
    "AuthError",
    "RateLimitError",
    "BrowserNotReadyError",
]
