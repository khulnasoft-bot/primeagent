import asyncio
from types import SimpleNamespace

import pytest
import wfx_rea.client as client_module
from wfx_rea.client import ReaAdapterError, ReaCapabilityError, ReaMcpClient


class FixtureTransport:
    def __init__(self):
        self.closed = False

    async def __aenter__(self):
        return "read-stream", "write-stream"

    async def __aexit__(self, *_args):
        self.closed = True


class FixtureSession:
    def __init__(self, _read_stream=None, _write_stream=None, *, tools=None, result=None, blocked_call=None):
        self.tools = tools or ["open_binary", "binary_overview"]
        self.result = result or SimpleNamespace(
            isError=False, structuredContent={"normalized_result": {"ok": True}}, content=[]
        )
        self.blocked_call = blocked_call
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    async def initialize(self):
        return SimpleNamespace(serverInfo=SimpleNamespace(name="rea-fixture", version="1.0"))

    async def list_tools(self):
        return SimpleNamespace(tools=[SimpleNamespace(name=name) for name in self.tools])

    async def call_tool(self, name, arguments):
        self.calls.append((name, arguments))
        if name == "open_binary":
            return SimpleNamespace(isError=False, structuredContent={}, content=[])
        if self.blocked_call is not None and name == "binary_overview":
            await self.blocked_call()
        return self.result


def _wire_fixture(monkeypatch, tmp_path, *, tools=None, result=None, blocked_call=None):
    target = tmp_path / "fixture.bin"
    target.write_bytes(b"fixture")
    monkeypatch.setenv("REA_ALLOWED_TARGET_ROOTS", str(tmp_path))
    transport = FixtureTransport()
    session = FixtureSession(tools=tools, result=result, blocked_call=blocked_call)
    monkeypatch.setattr(client_module, "stdio_client", lambda _parameters: transport)
    monkeypatch.setattr(client_module, "ClientSession", lambda *_streams: session)
    return target, transport, session


@pytest.mark.asyncio
async def test_mcp_call_discovers_capability_opens_target_and_preserves_provenance(monkeypatch, tmp_path):
    target, transport, session = _wire_fixture(monkeypatch, tmp_path)

    result = await ReaMcpClient(timeout_seconds=2).call("binary_overview", str(target))

    assert result.status == "complete"
    assert result.server_name == "rea-fixture"
    assert result.server_version == "1.0"
    assert result.structured_content == {"normalized_result": {"ok": True}}
    assert session.calls == [
        ("open_binary", {"path": str(target.resolve())}),
        ("binary_overview", {}),
    ]
    assert transport.closed


@pytest.mark.asyncio
async def test_mcp_call_fails_when_live_capability_is_missing(monkeypatch, tmp_path):
    target, transport, _session = _wire_fixture(monkeypatch, tmp_path, tools=["open_binary"])

    with pytest.raises(ReaCapabilityError, match="missing required tools"):
        await ReaMcpClient(timeout_seconds=2).call("binary_overview", str(target))

    assert transport.closed


@pytest.mark.asyncio
async def test_mcp_call_preserves_partial_results(monkeypatch, tmp_path):
    partial_result = SimpleNamespace(
        isError=True,
        structuredContent={"normalized_result": {"partial": True}},
        content=[],
    )
    target, _transport, _session = _wire_fixture(monkeypatch, tmp_path, result=partial_result)

    evidence = await ReaMcpClient(timeout_seconds=2).call("binary_overview", str(target))

    assert evidence.status == "partial"
    assert evidence.structured_content == {"normalized_result": {"partial": True}}
    assert evidence.error


@pytest.mark.asyncio
async def test_mcp_call_cancellation_closes_the_transport(monkeypatch, tmp_path):
    started = asyncio.Event()
    target, transport, _session = _wire_fixture(
        monkeypatch,
        tmp_path,
        blocked_call=lambda: started.set() or asyncio.Event().wait(),
    )
    operation = asyncio.create_task(ReaMcpClient(timeout_seconds=30).call("binary_overview", str(target)))
    await started.wait()
    operation.cancel()

    with pytest.raises(asyncio.CancelledError):
        await operation

    assert transport.closed


@pytest.mark.asyncio
async def test_mcp_call_timeout_closes_the_transport(monkeypatch, tmp_path):
    started = asyncio.Event()
    target, transport, _session = _wire_fixture(
        monkeypatch,
        tmp_path,
        blocked_call=lambda: started.set() or asyncio.Event().wait(),
    )

    with pytest.raises(ReaAdapterError, match="timeout"):
        await ReaMcpClient(timeout_seconds=1).call("binary_overview", str(target))

    assert started.is_set()
    assert transport.closed
