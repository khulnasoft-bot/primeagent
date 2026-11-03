"""Bounded stdio MCP adapter for REA's documented read-only analysis tools."""

from __future__ import annotations

import asyncio
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import BaseModel, ConfigDict, Field

DEFAULT_TIMEOUT_SECONDS = 120
DEFAULT_MAX_OUTPUT_BYTES = 10 * 1024 * 1024
_SUBPROCESS_ENV_NAMES = frozenset(
    {"PATH", "HOME", "TMP", "TMPDIR", "TEMP", "USERPROFILE", "APPDATA", "LANG", "LC_ALL", "SYSTEMROOT", "WINDIR"}
)
_SUBPROCESS_ENV_PREFIXES = ("REA_", "HOPPER_", "GHIDRA_", "IDA_", "RIZIN_", "CUTTER_", "KUNA_", "JEB_")
ALLOWED_READ_ONLY_TOOLS = frozenset(
    {
        "binary_session",
        "binary_overview",
        "search_procedures",
        "procedure_pseudo_code",
        "get_call_graph",
        "inspect_analysis_view",
    }
)


class ReaAdapterError(RuntimeError):
    """Base exception for REA adapter failures."""


class ReaAuthorizationError(ReaAdapterError):
    """Raised when the target is outside the configured authorization roots."""


class ReaCapabilityError(ReaAdapterError):
    """Raised when the REA server does not advertise a required tool."""


def rea_subprocess_environment() -> dict[str, str]:
    """Pass only runtime/provider settings, not unrelated PrimeAgent secrets."""
    explicit = {name.strip() for name in os.getenv("REA_SUBPROCESS_ENV_ALLOWLIST", "").split(",") if name.strip()}
    return {
        name: value
        for name, value in os.environ.items()
        if name in _SUBPROCESS_ENV_NAMES or name in explicit or name.startswith(_SUBPROCESS_ENV_PREFIXES)
    }


class ReaEvidence(BaseModel):
    """Normalized result retaining the original REA response and its provenance."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["complete", "partial"]
    tool: str
    target_path: str
    observed_at: datetime
    server_name: str | None = None
    server_version: str | None = None
    structured_content: Any = None
    content: list[dict[str, Any]] = Field(default_factory=list)
    error: str | None = None


def authorize_target_path(target_path: str, allowed_roots: str | None = None) -> Path:
    """Resolve a local target and require it to be inside an operator-approved root."""
    if not target_path or not target_path.strip():
        msg = "REA target path must not be empty."
        raise ReaAuthorizationError(msg)
    configured_roots = allowed_roots if allowed_roots is not None else os.getenv("REA_ALLOWED_TARGET_ROOTS", "")
    roots = [root.strip() for root in configured_roots.split(os.pathsep) if root.strip()]
    if not roots:
        msg = "Set REA_ALLOWED_TARGET_ROOTS to authorize REA target paths."
        raise ReaAuthorizationError(msg)

    try:
        target = Path(target_path).expanduser().resolve(strict=True)
        resolved_roots = [Path(root).expanduser().resolve(strict=True) for root in roots]
    except (OSError, RuntimeError) as exc:
        msg = f"REA target or authorization root is unavailable: {exc}"
        raise ReaAuthorizationError(msg) from exc

    if not target.is_file() and not target.is_dir():
        msg = "REA targets must be existing regular files or directories."
        raise ReaAuthorizationError(msg)
    if not any(target == root or root in target.parents for root in resolved_roots):
        msg = "REA target is outside REA_ALLOWED_TARGET_ROOTS."
        raise ReaAuthorizationError(msg)

    try:
        max_bytes = int(os.getenv("REA_MAX_TARGET_BYTES", str(2 * 1024 * 1024 * 1024)))
    except ValueError as exc:
        msg = "REA_MAX_TARGET_BYTES must be an integer."
        raise ReaAuthorizationError(msg) from exc
    if max_bytes < 1:
        msg = "REA_MAX_TARGET_BYTES must be positive."
        raise ReaAuthorizationError(msg)
    if target.is_file() and target.stat().st_size > max_bytes:
        msg = f"REA target exceeds the configured {max_bytes}-byte limit."
        raise ReaAuthorizationError(msg)
    if target.is_dir():
        _validate_directory_target(target, max_bytes)
    return target


def _validate_directory_target(target: Path, max_bytes: int) -> None:
    try:
        max_entries = int(os.getenv("REA_MAX_TARGET_ENTRIES", "100000"))
    except ValueError as exc:
        msg = "REA_MAX_TARGET_ENTRIES must be an integer."
        raise ReaAuthorizationError(msg) from exc
    if max_entries < 1:
        msg = "REA_MAX_TARGET_ENTRIES must be positive."
        raise ReaAuthorizationError(msg)

    entries = 0
    total_bytes = 0

    def fail_walk(error: OSError) -> None:
        msg = f"REA target directory could not be completely inspected: {error}"
        raise ReaAuthorizationError(msg) from error

    for current_root, directories, filenames in os.walk(target, followlinks=False, onerror=fail_walk):
        root = Path(current_root)
        for directory in directories:
            path = root / directory
            if path.is_symlink():
                msg = "REA target directories must not contain symlinks."
                raise ReaAuthorizationError(msg)
            entries += 1
        for filename in filenames:
            path = root / filename
            if path.is_symlink() or not path.is_file():
                msg = "REA target directories may contain only regular files and directories."
                raise ReaAuthorizationError(msg)
            entries += 1
            try:
                total_bytes += path.stat().st_size
            except OSError as exc:
                msg = f"REA target file could not be inspected: {path}"
                raise ReaAuthorizationError(msg) from exc
        if entries >= max_entries:
            msg = f"REA target exceeds the configured {max_entries}-entry limit."
            raise ReaAuthorizationError(msg)
        if total_bytes > max_bytes:
            msg = f"REA target exceeds the configured {max_bytes}-byte limit."
            raise ReaAuthorizationError(msg)


def validate_tool_arguments(tool: str, arguments: dict[str, Any]) -> None:
    """Reject REA inputs that could escape the target path authorization boundary."""
    if len(json.dumps(arguments, separators=(",", ":")).encode("utf-8")) > DEFAULT_MAX_OUTPUT_BYTES:
        msg = f"REA arguments exceed the {DEFAULT_MAX_OUTPUT_BYTES}-byte limit."
        raise ReaAdapterError(msg)
    if tool == "inspect_analysis_view":
        source = arguments.get("source")
        if (
            not isinstance(source, dict)
            or source.get("kind") != "inline"
            or not isinstance(source.get("evidence"), dict)
        ):
            msg = "REA analysis views must use inline evidence, not local file references."
            raise ReaAuthorizationError(msg)


def _process_parameters() -> StdioServerParameters:
    command = os.getenv("REA_MCP_COMMAND", "rea").strip()
    raw_args = os.getenv("REA_MCP_ARGS", '["mcp"]')
    if not command:
        msg = "REA_MCP_COMMAND must name an installed REA executable."
        raise ReaAdapterError(msg)
    try:
        args = json.loads(raw_args)
    except json.JSONDecodeError as exc:
        msg = "REA_MCP_ARGS must be a JSON array of strings."
        raise ReaAdapterError(msg) from exc
    if not isinstance(args, list) or not all(isinstance(arg, str) for arg in args):
        msg = "REA_MCP_ARGS must be a JSON array of strings."
        raise ReaAdapterError(msg)
    return StdioServerParameters(
        command=command,
        args=args,
        env=rea_subprocess_environment(),
        cwd=str(Path.home()),
    )


def _response_content(result: Any) -> list[dict[str, Any]]:
    content: list[dict[str, Any]] = []
    for block in getattr(result, "content", []) or []:
        if hasattr(block, "model_dump"):
            content.append(block.model_dump(mode="json", exclude_none=True))
        elif isinstance(block, dict):
            content.append(block)
        else:
            content.append({"type": type(block).__name__, "text": str(block)})
    return content


def normalize_result(tool: str, target: Path, result: Any, server_info: Any = None) -> ReaEvidence:
    """Normalize an MCP result without discarding REA's original evidence fields."""
    structured = getattr(result, "structuredContent", None)
    content = _response_content(result)
    if structured is None:
        for block in content:
            if block.get("type") == "text" and isinstance(block.get("text"), str):
                try:
                    structured = json.loads(block["text"])
                except json.JSONDecodeError:
                    continue
                break

    server_name = getattr(server_info, "name", None)
    server_version = getattr(server_info, "version", None)
    return ReaEvidence(
        status="partial" if getattr(result, "isError", False) else "complete",
        tool=tool,
        target_path=str(target),
        observed_at=datetime.now(UTC),
        server_name=server_name,
        server_version=server_version,
        structured_content=structured,
        content=content,
        error="REA reported a partial tool result." if getattr(result, "isError", False) else None,
    )


class ReaMcpClient:
    """Own one REA process for one workflow-node operation, then close it."""

    def __init__(self, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> None:
        if timeout_seconds < 1:
            msg = "timeout_seconds must be at least one"
            raise ValueError(msg)
        self.timeout_seconds = timeout_seconds

    async def call(self, tool: str, target_path: str, arguments: dict[str, Any] | None = None) -> ReaEvidence:
        if tool not in ALLOWED_READ_ONLY_TOOLS:
            msg = f"REA tool {tool!r} is not enabled by this read-only adapter."
            raise ReaCapabilityError(msg)
        target = authorize_target_path(target_path)
        tool_arguments = arguments or {}
        if not isinstance(tool_arguments, dict):
            msg = "REA tool arguments must be a JSON object."
            raise TypeError(msg)
        validate_tool_arguments(tool, tool_arguments)

        try:
            return await asyncio.wait_for(
                self._call_in_session(tool, target, tool_arguments),
                timeout=self.timeout_seconds,
            )
        except asyncio.TimeoutError as exc:
            msg = f"REA operation exceeded the {self.timeout_seconds}-second timeout."
            raise ReaAdapterError(msg) from exc
        except asyncio.CancelledError:
            raise
        except ReaAdapterError:
            raise
        except Exception as exc:
            msg = f"REA MCP operation failed: {type(exc).__name__}: {exc}"
            raise ReaAdapterError(msg) from exc

    async def _call_in_session(self, tool: str, target: Path, arguments: dict[str, Any]) -> ReaEvidence:
        async with (
            stdio_client(_process_parameters()) as (read_stream, write_stream),
            ClientSession(read_stream, write_stream) as session,
        ):
            initialized = await session.initialize()
            available = {item.name for item in (await session.list_tools()).tools}
            missing = {"open_binary", tool} - available
            if missing:
                msg = f"REA server is missing required tools: {', '.join(sorted(missing))}."
                raise ReaCapabilityError(msg)

            opened = await session.call_tool("open_binary", {"path": str(target)})
            if getattr(opened, "isError", False):
                msg = "REA refused to open the authorized target."
                raise ReaAdapterError(msg)
            result = await session.call_tool(tool, arguments)
            evidence = normalize_result(tool, target, result, getattr(initialized, "serverInfo", None))
            serialized_size = len(evidence.model_dump_json().encode("utf-8"))
            if serialized_size > DEFAULT_MAX_OUTPUT_BYTES:
                msg = (
                    f"REA response exceeds the {DEFAULT_MAX_OUTPUT_BYTES}-byte output limit; "
                    "evidence was not forwarded."
                )
                raise ReaAdapterError(msg)
            return evidence
