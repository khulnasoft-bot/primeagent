"""Custom exception types for PrimeAgent integration."""


class PrimeAgentIntegrationError(Exception):
    """Base exception for PrimeAgent integration errors."""

    pass


class ConversionError(PrimeAgentIntegrationError):
    """Error during PrimeAgent to Stepflow conversion."""

    pass


class ValidationError(PrimeAgentIntegrationError):
    """Error during workflow validation."""

    pass


class ExecutionError(PrimeAgentIntegrationError):
    """Error during component execution."""

    pass
