"""Scraper client — HTTP scraping without a browser."""

import time
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import requests
import httpx

from .exceptions import BaasError, AuthError, RateLimitError

logger = logging.getLogger("dawg_baas")

DEFAULT_BASE_URL = "https://dawgswarm.ru"


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class ScrapeResult:
    """Result of a single page scrape."""

    success: bool
    url: str
    final_url: str = ""
    status_code: int = 0
    content: str = ""
    metadata: Dict = field(default_factory=dict)
    links: Optional[List[str]] = None
    error: Optional[str] = None
    elapsed_ms: int = 0


@dataclass
class JobPage:
    """Single page result within a job."""

    url: str
    status_code: int = 0
    content: str = ""
    metadata: Dict = field(default_factory=dict)
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Job (sync)
# ---------------------------------------------------------------------------

class ScrapeJob:
    """Async job (crawl or batch) with sync polling."""

    def __init__(self, data: dict, requester):
        self._requester = requester
        self._update(data)

    def _update(self, data: dict):
        self.job_id: str = data.get("job_id", "")
        self.type: str = data.get("type", "")
        self.status: str = data.get("status", "running")
        self.progress: Dict = data.get("progress", {})
        self.pages: List[JobPage] = [
            JobPage(
                url=p.get("url", ""),
                status_code=p.get("status_code", 0),
                content=p.get("content", ""),
                metadata=p.get("metadata", {}),
                error=p.get("error"),
            )
            for p in data.get("pages", [])
        ]
        self.errors: List[str] = data.get("errors", [])
        self.created_at: str = data.get("created_at", "")
        self.completed_at: Optional[str] = data.get("completed_at")
        self.elapsed_ms: int = data.get("elapsed_ms", 0)

    def wait(self, timeout: float = 300, poll_interval: float = 2.0) -> "ScrapeJob":
        """Block until job completes or timeout."""
        start = time.time()
        while time.time() - start < timeout:
            if self.status != "running":
                return self
            time.sleep(poll_interval)
            self.refresh()
        raise BaasError(f"Job {self.job_id} not completed after {timeout}s")

    def refresh(self) -> "ScrapeJob":
        """Poll current status."""
        data = self._requester("GET", f"/api/v1/jobs/{self.job_id}")
        self._update(data)
        return self

    def cancel(self) -> None:
        """Cancel running job."""
        data = self._requester("DELETE", f"/api/v1/jobs/{self.job_id}")
        self._update(data)


# ---------------------------------------------------------------------------
# Job (async)
# ---------------------------------------------------------------------------

class AsyncScrapeJob:
    """Async job with async polling."""

    def __init__(self, data: dict, requester):
        self._requester = requester
        self._update(data)

    def _update(self, data: dict):
        self.job_id: str = data.get("job_id", "")
        self.type: str = data.get("type", "")
        self.status: str = data.get("status", "running")
        self.progress: Dict = data.get("progress", {})
        self.pages: List[JobPage] = [
            JobPage(
                url=p.get("url", ""),
                status_code=p.get("status_code", 0),
                content=p.get("content", ""),
                metadata=p.get("metadata", {}),
                error=p.get("error"),
            )
            for p in data.get("pages", [])
        ]
        self.errors: List[str] = data.get("errors", [])
        self.created_at: str = data.get("created_at", "")
        self.completed_at: Optional[str] = data.get("completed_at")
        self.elapsed_ms: int = data.get("elapsed_ms", 0)

    async def wait(self, timeout: float = 300, poll_interval: float = 2.0) -> "AsyncScrapeJob":
        """Wait until job completes."""
        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < timeout:
            if self.status != "running":
                return self
            await asyncio.sleep(poll_interval)
            await self.refresh()
        raise BaasError(f"Job {self.job_id} not completed after {timeout}s")

    async def refresh(self) -> "AsyncScrapeJob":
        """Poll current status."""
        data = await self._requester("GET", f"/api/v1/jobs/{self.job_id}")
        self._update(data)
        return self

    async def cancel(self) -> None:
        """Cancel running job."""
        data = await self._requester("DELETE", f"/api/v1/jobs/{self.job_id}")
        self._update(data)


# ---------------------------------------------------------------------------
# Scraper (sync)
# ---------------------------------------------------------------------------

class Scraper:
    """
    HTTP scraper client. No browser needed.

    Example:
        scraper = Scraper(api_key="your_key")
        result = scraper.scrape("https://example.com")
        print(result.content)

    Context manager:
        with Scraper(api_key="your_key") as s:
            result = s.scrape("https://example.com")
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 60.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self._session = requests.Session()
        self._session.headers["X-API-Key"] = api_key

    def scrape(
        self,
        url: str,
        format: str = "markdown",
        headers: Optional[Dict[str, str]] = None,
        timeout_ms: int = 30000,
        main_content: bool = False,
        include_links: bool = False,
    ) -> ScrapeResult:
        """
        Scrape a single URL and return extracted content.

        Args:
            url: Target URL to scrape.
            format: Output format — "markdown", "text", or "html".
            headers: Custom HTTP headers for the request.
            timeout_ms: Page fetch timeout in milliseconds.
            main_content: Strip boilerplate (nav, footer, ads).
            include_links: Include discovered links in result.

        Returns:
            ScrapeResult with content and metadata.
        """
        payload = {
            "url": url,
            "format": format,
            "timeout_ms": timeout_ms,
            "main_content": main_content,
            "include_links": include_links,
        }
        if headers:
            payload["headers"] = headers

        data = self._request("POST", "/api/v1/scrape", json=payload)
        return ScrapeResult(
            success=data.get("success", False),
            url=data.get("url", url),
            final_url=data.get("final_url", ""),
            status_code=data.get("status_code", 0),
            content=data.get("content", ""),
            metadata=data.get("metadata", {}),
            links=data.get("links"),
            error=data.get("error"),
            elapsed_ms=data.get("elapsed_ms", 0),
        )

    def crawl(
        self,
        url: str,
        format: str = "markdown",
        max_depth: int = 2,
        max_pages: int = 50,
        concurrency: int = 3,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        timeout_ms: int = 30000,
        main_content: bool = False,
    ) -> ScrapeJob:
        """
        Start a crawl job. Returns immediately with a ScrapeJob.
        Call job.wait() to block until completion.

        Args:
            url: Seed URL to start crawling from.
            format: Output format for each page.
            max_depth: Maximum link depth to follow.
            max_pages: Maximum pages to scrape.
            concurrency: Parallel fetch workers.
            include_patterns: URL glob patterns to include.
            exclude_patterns: URL glob patterns to exclude.
            timeout_ms: Per-page fetch timeout.
            main_content: Strip boilerplate from each page.
        """
        payload = {
            "url": url,
            "format": format,
            "max_depth": max_depth,
            "max_pages": max_pages,
            "concurrency": concurrency,
            "timeout_ms": timeout_ms,
            "main_content": main_content,
        }
        if include_patterns:
            payload["include_patterns"] = include_patterns
        if exclude_patterns:
            payload["exclude_patterns"] = exclude_patterns

        data = self._request("POST", "/api/v1/crawl", json=payload)
        return ScrapeJob(data, self._request)

    def batch(
        self,
        urls: List[str],
        format: str = "markdown",
        concurrency: int = 5,
        timeout_ms: int = 30000,
        main_content: bool = False,
    ) -> ScrapeJob:
        """
        Start a batch scrape job. Returns immediately with a ScrapeJob.
        Call job.wait() to block until completion.

        Args:
            urls: List of URLs to scrape.
            format: Output format for each page.
            concurrency: Parallel fetch workers.
            timeout_ms: Per-page fetch timeout.
            main_content: Strip boilerplate from each page.
        """
        data = self._request("POST", "/api/v1/batch", json={
            "urls": urls,
            "format": format,
            "concurrency": concurrency,
            "timeout_ms": timeout_ms,
            "main_content": main_content,
        })
        return ScrapeJob(data, self._request)

    def get_job(self, job_id: str) -> ScrapeJob:
        """Get job status by ID."""
        data = self._request("GET", f"/api/v1/jobs/{job_id}")
        return ScrapeJob(data, self._request)

    def cancel_job(self, job_id: str) -> None:
        """Cancel a running job."""
        self._request("DELETE", f"/api/v1/jobs/{job_id}")

    def close(self) -> None:
        """Close HTTP session."""
        self._session.close()

    def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make HTTP request with error handling."""
        try:
            resp = self._session.request(
                method, f"{self.base_url}{path}", timeout=self.timeout, **kwargs
            )
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

    def __enter__(self) -> "Scraper":
        return self

    def __exit__(self, *args) -> None:
        self.close()


# ---------------------------------------------------------------------------
# AsyncScraper
# ---------------------------------------------------------------------------

class AsyncScraper:
    """
    Async HTTP scraper client.

    Example:
        async with AsyncScraper(api_key="your_key") as s:
            result = await s.scrape("https://example.com")
            print(result.content)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 60.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers={"X-API-Key": self.api_key},
                timeout=self.timeout,
            )
        return self._client

    async def scrape(
        self,
        url: str,
        format: str = "markdown",
        headers: Optional[Dict[str, str]] = None,
        timeout_ms: int = 30000,
        main_content: bool = False,
        include_links: bool = False,
    ) -> ScrapeResult:
        """Scrape a single URL."""
        payload = {
            "url": url,
            "format": format,
            "timeout_ms": timeout_ms,
            "main_content": main_content,
            "include_links": include_links,
        }
        if headers:
            payload["headers"] = headers

        data = await self._request("POST", "/api/v1/scrape", json=payload)
        return ScrapeResult(
            success=data.get("success", False),
            url=data.get("url", url),
            final_url=data.get("final_url", ""),
            status_code=data.get("status_code", 0),
            content=data.get("content", ""),
            metadata=data.get("metadata", {}),
            links=data.get("links"),
            error=data.get("error"),
            elapsed_ms=data.get("elapsed_ms", 0),
        )

    async def crawl(
        self,
        url: str,
        format: str = "markdown",
        max_depth: int = 2,
        max_pages: int = 50,
        concurrency: int = 3,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        timeout_ms: int = 30000,
        main_content: bool = False,
    ) -> AsyncScrapeJob:
        """Start a crawl job."""
        payload = {
            "url": url,
            "format": format,
            "max_depth": max_depth,
            "max_pages": max_pages,
            "concurrency": concurrency,
            "timeout_ms": timeout_ms,
            "main_content": main_content,
        }
        if include_patterns:
            payload["include_patterns"] = include_patterns
        if exclude_patterns:
            payload["exclude_patterns"] = exclude_patterns

        data = await self._request("POST", "/api/v1/crawl", json=payload)
        return AsyncScrapeJob(data, self._request)

    async def batch(
        self,
        urls: List[str],
        format: str = "markdown",
        concurrency: int = 5,
        timeout_ms: int = 30000,
        main_content: bool = False,
    ) -> AsyncScrapeJob:
        """Start a batch scrape job."""
        data = await self._request("POST", "/api/v1/batch", json={
            "urls": urls,
            "format": format,
            "concurrency": concurrency,
            "timeout_ms": timeout_ms,
            "main_content": main_content,
        })
        return AsyncScrapeJob(data, self._request)

    async def get_job(self, job_id: str) -> AsyncScrapeJob:
        """Get job status by ID."""
        data = await self._request("GET", f"/api/v1/jobs/{job_id}")
        return AsyncScrapeJob(data, self._request)

    async def cancel_job(self, job_id: str) -> None:
        """Cancel a running job."""
        await self._request("DELETE", f"/api/v1/jobs/{job_id}")

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

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

    async def __aenter__(self) -> "AsyncScraper":
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()
