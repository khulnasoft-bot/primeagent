"""Exceptions raised by the PrimeAgent SDK."""

from __future__ import annotations


class PrimeAgentError(Exception):
    """Base class for all PrimeAgent SDK errors."""


class PrimeAgentHTTPError(PrimeAgentError):
    """An HTTP error was returned by the PrimeAgent API."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")


class PrimeAgentNotFoundError(PrimeAgentHTTPError):
    """The requested resource was not found (404)."""


class PrimeAgentAuthError(PrimeAgentHTTPError):
    """Authentication failed (401/403)."""


class PrimeAgentValidationError(PrimeAgentHTTPError):
    """The request payload was rejected by the server (422)."""


class PrimeAgentConnectionError(PrimeAgentError):
    """Could not connect to the PrimeAgent instance."""


class PrimeAgentTimeoutError(PrimeAgentError):
    """A background job or polling operation exceeded its timeout.

    Adapted from ``PrimeAgentV2TimeoutError`` in khulnasoft-bot/sdk PR #1
    (Janardan Singh Kavia, IBM Corp., Apache 2.0).
    """


class EnvironmentNotFoundError(PrimeAgentError):
    """The named environment is not defined in the environments config."""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(
            f"Environment {name!r} not found. Check your primeagent-environments.toml (or PRIMEAGENT_ENV variable)."
        )


class EnvironmentConfigError(PrimeAgentError):
    """The environments config file is malformed or missing required fields."""
