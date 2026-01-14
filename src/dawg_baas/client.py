"""BaaS client - simple access to browser pool."""

import time
import logging
from typing import Optional

import requests
import httpx

from .exceptions import BaasError, AuthError, RateLimitError, BrowserNotReadyError

logger = logging.getLogger("dawg_baas")

DEFAULT_BASE_URL = "https://dawgswarm.ru"


class Baas:
    """
    Simple BaaS client. Get browser, use it, release it.

    Example:
        baas = Baas(api_key="your_key")
        ws_url = baas.create()

        # Your code with any CDP framework (Playwright, Puppeteer, Selenium, etc.)
        browser = playwright.chromium.connect_over_cdp(ws_url)
        # ...

        baas.release()

    Context manager:
        with Baas(api_key="your_key") as ws_url:
            browser = playwright.chromium.connect_over_cdp(ws_url)
            # ...
        # auto-released

    With proxy:
        ws_url = baas.create(proxy="socks5://user:pass@host:port")
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 60.0,
        poll_interval: float = 2.0,
    ):
        """
        Args:
            api_key: Your BaaS API key.
            base_url: BaaS service URL.
            timeout: Max seconds to wait for browser ready.
            poll_interval: Seconds between ready checks.
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.poll_interval = poll_interval

        self._session = requests.Session()
        self._session.headers["X-API-Key"] = api_key

        self._browser_id: Optional[str] = None
        self._session_id: Optional[str] = None
        self._ephemeral_token: Optional[str] = None

    def create(self, proxy: Optional[str] = None) -> str:
        """
        Create browser and return ws_url.

        Args:
            proxy: Optional proxy URL (e.g., "socks5://user:pass@host:port")

        Returns:
            WebSocket URL for CDP connection.
        """
        # Parse proxy string if provided
        payload = {}
        if proxy:
            payload["proxy"] = self._parse_proxy(proxy)

        # Create browser
        resp = self._request("POST", "/api/v1/browsers", json=payload or None)
        data = resp.get("data", resp)

        self._browser_id = data.get("browserId") or data.get("browser_id")
        self._session_id = data.get("sessionId") or data.get("session_id")
        self._ephemeral_token = data.get("ephemeralToken") or data.get("ephemeral_token")

        # Wait for ready and get ws_url
        ws_url = self._wait_ready()
        return ws_url

    def release(self) -> None:
        """Release browser back to pool."""
        if self._session_id:
            try:
                self._request("DELETE", f"/api/v1/browsers/{self._session_id}")
            except BaasError as e:
                logger.warning(f"Failed to release browser: {e}")
            finally:
                self._browser_id = None
                self._session_id = None
                self._ephemeral_token = None

    def close(self) -> None:
        """Close HTTP session."""
        self._session.close()

    def _wait_ready(self) -> str:
        """Poll until browser is ready, return ws_url."""
        start = time.time()

        while time.time() - start < self.timeout:
            try:
                resp = self._request("GET", f"/dawg/baas/{self._browser_id}/json/version")
                ws_debugger = resp.get("webSocketDebuggerUrl", "")

                if "/devtools/" in ws_debugger:
                    devtools_path = ws_debugger.split("/devtools/", 1)[1]
                    ws_base = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
                    # Use ephemeral token if available (preferred), fallback to apiKey
                    if self._ephemeral_token:
                        return f"{ws_base}/dawg/baas/{self._browser_id}/devtools/{devtools_path}?token={self._ephemeral_token}"
                    else:
                        return f"{ws_base}/dawg/baas/{self._browser_id}/devtools/{devtools_path}?apiKey={self.api_key}"

            except BaasError as e:
                if e.status_code == 502:
                    time.sleep(self.poll_interval)
                    continue
                raise

        raise BrowserNotReadyError(f"Browser not ready after {self.timeout}s")

    def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make HTTP request with error handling."""
        try:
            resp = self._session.request(method, f"{self.base_url}{path}", timeout=30, **kwargs)
        except requests.RequestException as e:
            raise BaasError(f"Connection failed: {e}")

        if resp.status_code == 401:
            raise AuthError("Invalid API key", status_code=401)
        if resp.status_code == 429:
            data = resp.json() if resp.text else {}
            retry = data.get("detail", {}).get("retry_after_seconds", 60)
            raise RateLimitError("Rate limit exceeded", retry_after=retry, status_code=429)
        if resp.status_code >= 400:
            raise BaasError(f"API error: {resp.status_code}", status_code=resp.status_code)

        return resp.json() if resp.text else {}

    def _parse_proxy(self, proxy: str) -> dict:
        """Parse proxy string to dict."""
        # Format: protocol://user:pass@host:port or protocol://host:port
        result = {"server": proxy}

        if "@" in proxy:
            # Has auth
            proto_auth, host_port = proxy.rsplit("@", 1)
            proto, auth = proto_auth.split("://", 1)
            if ":" in auth:
                user, passwd = auth.split(":", 1)
                result["server"] = f"{proto}://{host_port}"
                result["username"] = user
                result["password"] = passwd

        return result

    @property
    def browser_id(self) -> Optional[str]:
        """Current browser ID."""
        return self._browser_id

    @property
    def session_id(self) -> Optional[str]:
        """Current session ID."""
        return self._session_id

    def __enter__(self) -> str:
        return self.create()

    def __exit__(self, *args) -> None:
        self.release()
        self.close()


class AsyncBaas:
    """
    Async BaaS client.

    Example:
        baas = AsyncBaas(api_key="your_key")
        ws_url = await baas.create()
        # ... your async code ...
        await baas.release()

        # Or with context manager:
        async with AsyncBaas(api_key="your_key") as ws_url:
            # ...
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 60.0,
        poll_interval: float = 2.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.poll_interval = poll_interval

        self._client: Optional[httpx.AsyncClient] = None
        self._browser_id: Optional[str] = None
        self._session_id: Optional[str] = None
        self._ephemeral_token: Optional[str] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers={"X-API-Key": self.api_key},
                timeout=30,
            )
        return self._client

    async def create(self, proxy: Optional[str] = None) -> str:
        """Create browser and return ws_url."""
        payload = {}
        if proxy:
            payload["proxy"] = self._parse_proxy(proxy)

        resp = await self._request("POST", "/api/v1/browsers", json=payload or None)
        data = resp.get("data", resp)

        self._browser_id = data.get("browserId") or data.get("browser_id")
        self._session_id = data.get("sessionId") or data.get("session_id")
        self._ephemeral_token = data.get("ephemeralToken") or data.get("ephemeral_token")

        ws_url = await self._wait_ready()
        return ws_url

    async def release(self) -> None:
        """Release browser."""
        if self._session_id:
            try:
                await self._request("DELETE", f"/api/v1/browsers/{self._session_id}")
            except BaasError as e:
                logger.warning(f"Failed to release: {e}")
            finally:
                self._browser_id = None
                self._session_id = None
                self._ephemeral_token = None

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _wait_ready(self) -> str:
        """Poll until ready."""
        import asyncio

        start = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start < self.timeout:
            try:
                resp = await self._request("GET", f"/dawg/baas/{self._browser_id}/json/version")
                ws_debugger = resp.get("webSocketDebuggerUrl", "")

                if "/devtools/" in ws_debugger:
                    devtools_path = ws_debugger.split("/devtools/", 1)[1]
                    ws_base = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
                    # Use ephemeral token if available (preferred), fallback to apiKey
                    if self._ephemeral_token:
                        return f"{ws_base}/dawg/baas/{self._browser_id}/devtools/{devtools_path}?token={self._ephemeral_token}"
                    else:
                        return f"{ws_base}/dawg/baas/{self._browser_id}/devtools/{devtools_path}?apiKey={self.api_key}"

            except BaasError as e:
                if e.status_code == 502:
                    await asyncio.sleep(self.poll_interval)
                    continue
                raise

        raise BrowserNotReadyError(f"Browser not ready after {self.timeout}s")

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make async HTTP request."""
        client = await self._get_client()

        try:
            resp = await client.request(method, f"{self.base_url}{path}", **kwargs)
        except httpx.RequestError as e:
            raise BaasError(f"Connection failed: {e}")

        if resp.status_code == 401:
            raise AuthError("Invalid API key", status_code=401)
        if resp.status_code == 429:
            data = resp.json() if resp.text else {}
            retry = data.get("detail", {}).get("retry_after_seconds", 60)
            raise RateLimitError("Rate limit exceeded", retry_after=retry, status_code=429)
        if resp.status_code >= 400:
            raise BaasError(f"API error: {resp.status_code}", status_code=resp.status_code)

        return resp.json() if resp.text else {}

    def _parse_proxy(self, proxy: str) -> dict:
        """Parse proxy string."""
        result = {"server": proxy}
        if "@" in proxy:
            proto_auth, host_port = proxy.rsplit("@", 1)
            proto, auth = proto_auth.split("://", 1)
            if ":" in auth:
                user, passwd = auth.split(":", 1)
                result["server"] = f"{proto}://{host_port}"
                result["username"] = user
                result["password"] = passwd
        return result

    @property
    def browser_id(self) -> Optional[str]:
        return self._browser_id

    @property
    def session_id(self) -> Optional[str]:
        return self._session_id

    async def __aenter__(self) -> str:
        return await self.create()

    async def __aexit__(self, *args) -> None:
        await self.release()
        await self.close()
