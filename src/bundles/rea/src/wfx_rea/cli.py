"""Bounded one-shot CLI fallback for REA operations with documented commands."""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
import signal
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from wfx_rea.client import (
    DEFAULT_MAX_OUTPUT_BYTES,
    DEFAULT_TIMEOUT_SECONDS,
    ReaAdapterError,
    ReaEvidence,
    authorize_target_path,
    rea_subprocess_environment,
)

_MAX_STDERR_BYTES = 64 * 1024
_CLI_COMMANDS = {
    "binary_session": "inspect",
    "binary_overview": "inspect",
    "procedure_pseudo_code": "decompile",
    "search_procedures": "search",
    "inspect_analysis_view": "inspect-analysis-view",
}


def build_cli_arguments(tool: str, target: Path, arguments: dict[str, Any]) -> list[str]:
    """Map only supported REA operations to documented positional CLI commands."""
    command = _CLI_COMMANDS.get(tool)
    if command is None:
        msg = f"REA CLI fallback does not support {tool!r}; use the MCP transport."
        raise ReaAdapterError(msg)
    if command == "inspect":
        operation_arguments = [command, str(target)]
    elif command == "decompile":
        procedure = arguments.get("procedure") or arguments.get("address")
        if not isinstance(procedure, str) or not procedure.strip():
            msg = "REA decompile fallback requires a procedure or address argument."
            raise ReaAdapterError(msg)
        operation_arguments = [command, str(target), f"--procedure={procedure}"]
    elif command == "search":
        pattern = arguments.get("pattern")
        if not isinstance(pattern, str) or not pattern:
            msg = "REA search fallback requires a pattern argument."
            raise ReaAdapterError(msg)
        operation_arguments = [command, str(target), f"--pattern={pattern}", "--kind=procedures"]
    else:
        from wfx_rea.client import validate_tool_arguments

        validate_tool_arguments(tool, arguments)
        operation_arguments = [command, json.dumps(arguments, separators=(",", ":"))]
    return [*operation_arguments, "--json"]


async def _read_bounded(stream: asyncio.StreamReader, limit: int, *, truncate: bool = False) -> bytes:
    collected = bytearray()
    while chunk := await stream.read(64 * 1024):
        if len(collected) + len(chunk) > limit:
            if not truncate:
                msg = f"REA CLI output exceeds the configured {limit}-byte limit."
                raise ReaAdapterError(msg)
            collected.extend(chunk[: limit - len(collected)])
            continue
        collected.extend(chunk)
    return bytes(collected)


class ReaCliClient:
    """Run supported REA commands without a shell and always reap the child process."""

    def __init__(self, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> None:
        if timeout_seconds < 1:
            msg = "timeout_seconds must be at least one"
            raise ValueError(msg)
        self.timeout_seconds = timeout_seconds

    async def call(self, tool: str, target_path: str, arguments: dict[str, Any] | None = None) -> ReaEvidence:
        target = authorize_target_path(target_path)
        argv = build_cli_arguments(tool, target, arguments or {})
        command = os.getenv("REA_CLI_COMMAND", "rea").strip()
        if not command:
            msg = "REA_CLI_COMMAND must name an installed REA executable."
            raise ReaAdapterError(msg)

        process: asyncio.subprocess.Process | None = None
        stdout_task: asyncio.Task[bytes] | None = None
        stderr_task: asyncio.Task[bytes] | None = None
        try:
            process = await asyncio.create_subprocess_exec(
                command,
                *argv,
                cwd=str(Path.home()),
                env=rea_subprocess_environment(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                start_new_session=os.name == "posix",
            )
            if process.stdout is None or process.stderr is None:
                msg = "REA CLI process pipes could not be opened."
                raise ReaAdapterError(msg)
            stdout_task = asyncio.create_task(_read_bounded(process.stdout, DEFAULT_MAX_OUTPUT_BYTES))
            stderr_task = asyncio.create_task(_read_bounded(process.stderr, _MAX_STDERR_BYTES, truncate=True))
            _, stdout, stderr = await asyncio.wait_for(
                asyncio.gather(process.wait(), stdout_task, stderr_task),
                timeout=self.timeout_seconds,
            )
        except asyncio.TimeoutError as exc:
            msg = f"REA CLI operation exceeded the {self.timeout_seconds}-second timeout."
            raise ReaAdapterError(msg) from exc
        except asyncio.CancelledError:
            raise
        except ReaAdapterError:
            raise
        except Exception as exc:
            msg = f"REA CLI operation failed: {type(exc).__name__}: {exc}"
            raise ReaAdapterError(msg) from exc
        finally:
            if process is not None and process.returncode is None:
                if os.name == "posix":
                    with contextlib.suppress(ProcessLookupError):
                        os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
                await process.wait()
            for task in (stdout_task, stderr_task):
                if task is not None and not task.done():
                    task.cancel()
                    await asyncio.gather(task, return_exceptions=True)

        try:
            result = json.loads(stdout)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            msg = "REA CLI did not return valid JSON evidence."
            raise ReaAdapterError(msg) from exc
        return ReaEvidence(
            status="complete" if process.returncode == 0 else "partial",
            tool=tool,
            target_path=str(target),
            observed_at=datetime.now(UTC),
            structured_content=result,
            content=[{"type": "text", "text": stderr.decode("utf-8", errors="replace")}] if stderr else [],
            error=None if process.returncode == 0 else f"REA CLI exited with status {process.returncode}.",
        )
