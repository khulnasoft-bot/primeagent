"""primeagent-sdk -- Python SDK for the PrimeAgent REST API."""

from primeagent_sdk._async_client import AsyncClient, AsyncPrimeAgentClient
from primeagent_sdk.background_job import BackgroundJob
from primeagent_sdk.client import Client, PrimeAgentClient
from primeagent_sdk.environments import (
    EnvironmentConfig,
    get_async_client,
    get_client,
    get_environment,
    load_environments,
)
from primeagent_sdk.exceptions import (
    EnvironmentConfigError,
    EnvironmentNotFoundError,
    PrimeAgentAuthError,
    PrimeAgentConnectionError,
    PrimeAgentError,
    PrimeAgentHTTPError,
    PrimeAgentNotFoundError,
    PrimeAgentTimeoutError,
    PrimeAgentValidationError,
)
from primeagent_sdk.models import (
    Flow,
    FlowCreate,
    FlowUpdate,
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectWithFlows,
    RunOutput,
    RunRequest,
    RunResponse,
    StreamChunk,
)
from primeagent_sdk.serialization import flow_to_json, normalize_flow, normalize_flow_file

__all__ = [
    "AsyncClient",  # short alias for AsyncPrimeAgentClient (preferred)
    "AsyncPrimeAgentClient",
    "BackgroundJob",
    "Client",  # short alias for PrimeAgentClient (preferred)
    "EnvironmentConfig",
    "EnvironmentConfigError",
    "EnvironmentNotFoundError",
    "Flow",
    "FlowCreate",
    "FlowUpdate",
    "PrimeAgentAuthError",
    "PrimeAgentClient",
    "PrimeAgentConnectionError",
    "PrimeAgentError",
    "PrimeAgentHTTPError",
    "PrimeAgentNotFoundError",
    "PrimeAgentTimeoutError",
    "PrimeAgentValidationError",
    "Project",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectWithFlows",
    "RunOutput",
    "RunRequest",
    "RunResponse",
    "StreamChunk",
    "flow_to_json",
    "get_async_client",
    "get_client",
    "get_environment",
    "load_environments",
    "normalize_flow",
    "normalize_flow_file",
]
