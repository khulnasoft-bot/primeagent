import os
import sys
from pathlib import Path

import pytest
from wfx_rea.cli import build_cli_arguments
from wfx_rea.cli import ReaCliClient
from wfx_rea.client import ReaAdapterError


def test_cli_decompile_uses_the_documented_procedure_selector(tmp_path):
    target = tmp_path / "sample.bin"

    assert build_cli_arguments("procedure_pseudo_code", target, {"procedure": "main"}) == [
        "decompile",
        str(target),
        "--procedure=main",
        "--json",
    ]


def test_cli_search_is_limited_to_procedure_names(tmp_path):
    target = tmp_path / "sample.bin"

    assert build_cli_arguments("search_procedures", target, {"pattern": "entry"}) == [
        "search",
        str(target),
        "--pattern=entry",
        "--kind=procedures",
        "--json",
    ]


def test_cli_fallback_refuses_operations_without_a_documented_cli_mapping(tmp_path):
    with pytest.raises(ReaAdapterError, match="does not support"):
        build_cli_arguments("get_call_graph", tmp_path / "sample.bin", {})


def test_cli_decompile_requires_a_selector(tmp_path):
    with pytest.raises(ReaAdapterError, match="requires a procedure"):
        build_cli_arguments("procedure_pseudo_code", tmp_path / "sample.bin", {})


def test_cli_analysis_view_refuses_local_file_sources(tmp_path):
    from wfx_rea.client import ReaAuthorizationError

    with pytest.raises(ReaAuthorizationError, match="inline evidence"):
        build_cli_arguments(
            "inspect_analysis_view",
            tmp_path / "sample.bin",
            {"source": {"kind": "file", "path": "/outside/evidence.json"}},
        )


@pytest.mark.asyncio
@pytest.mark.skipif(os.name == "nt", reason="Fixture executable uses a POSIX shebang.")
async def test_cli_client_runs_a_controlled_fixture_and_normalizes_evidence(monkeypatch, tmp_path):
    target = tmp_path / "sample.bin"
    target.write_bytes(b"fixture")
    executable = tmp_path / "rea-fixture"
    executable.write_text(
        f"#!{sys.executable}\nimport json\nprint(json.dumps({{'normalized_result': {{'fixture': True}}}}))\n",
        encoding="utf-8",
    )
    executable.chmod(0o700)
    monkeypatch.setenv("REA_ALLOWED_TARGET_ROOTS", str(tmp_path))
    monkeypatch.setenv("REA_CLI_COMMAND", str(executable))

    evidence = await ReaCliClient(timeout_seconds=3).call("binary_overview", str(target))

    assert evidence.status == "complete"
    assert evidence.structured_content == {"normalized_result": {"fixture": True}}
    assert evidence.target_path == str(target.resolve())


@pytest.mark.asyncio
@pytest.mark.skipif(os.name == "nt", reason="Fixture executable uses a POSIX shebang.")
async def test_cli_timeout_reaps_the_owned_process(monkeypatch, tmp_path):
    target = tmp_path / "sample.bin"
    target.write_bytes(b"fixture")
    executable = tmp_path / "rea-slow-fixture"
    executable.write_text(f"#!{sys.executable}\nimport time\ntime.sleep(30)\n", encoding="utf-8")
    executable.chmod(0o700)
    monkeypatch.setenv("REA_ALLOWED_TARGET_ROOTS", str(tmp_path))
    monkeypatch.setenv("REA_CLI_COMMAND", str(executable))

    with pytest.raises(ReaAdapterError, match="timeout"):
        await ReaCliClient(timeout_seconds=1).call("binary_overview", str(target))
