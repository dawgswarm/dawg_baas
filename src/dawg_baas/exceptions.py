"""Exceptions for BaaS SDK."""


class BaasError(Exception):
    """Base exception."""

    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthError(BaasError):
    """Invalid API key (401)."""
    pass


class RateLimitError(BaasError):
    """Rate limit exceeded (429)."""

    def __init__(self, message: str, retry_after: int = 60, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class BrowserNotReadyError(BaasError):
    """Browser didn't start in time."""
    pass
