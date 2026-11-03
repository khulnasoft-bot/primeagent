"""WFX components that call REA without exposing arbitrary MCP operations."""

from __future__ import annotations

import json
from typing import Any

from wfx.custom.custom_component.component import Component
from wfx.io import DictInput, DropdownInput, IntInput, JSONInput, Output, StrInput
from wfx.schema.data import Data

from wfx_rea.cli import ReaCliClient
from wfx_rea.client import ReaMcpClient, authorize_target_path

_COMMON_INPUTS = [
    StrInput(
        name="target_path",
        display_name="Authorized Target Path",
        info="Existing local file or directory under REA_ALLOWED_TARGET_ROOTS.",
        required=True,
    ),
    DropdownInput(
        name="transport",
        display_name="REA Transport",
        options=["mcp", "cli"],
        value="mcp",
        info="CLI supports overview, procedure search/decompilation, and evidence-view commands only.",
        advanced=True,
    ),
    DictInput(name="arguments", display_name="REA Tool Arguments", value={}),
    IntInput(
        name="timeout_seconds",
        display_name="Timeout (seconds)",
        value=120,
        range_spec={"min": 1, "max": 3600, "step": 1},
        advanced=True,
    ),
]
_ANALYSIS_INPUTS = [*_COMMON_INPUTS, JSONInput(name="validation", display_name="Validated Target", required=True)]


class ReaNodeComponent(Component):
    """Shared execution helper for fixed-purpose REA analysis nodes."""

    def build(self, **kwargs) -> None:
        self.set_attributes(kwargs)

    async def _invoke_async(self, tool: str, arguments: dict[str, Any] | None = None) -> Data:
        if tool != "binary_session":
            validation = self.validation
            if isinstance(validation, Data):
                validation = validation.data
            if not isinstance(validation, dict) or validation.get("status") != "complete":
                raise ValueError("Connect a successful REA Target Validation output before analysis.")
            authorized_path = authorize_target_path(str(self.target_path))
            if validation.get("target_path") != str(authorized_path):
                raise ValueError("REA validation output does not match the configured target path.")

        timeout_seconds = int(self.timeout_seconds or 120)
        client = ReaCliClient(timeout_seconds) if self.transport == "cli" else ReaMcpClient(timeout_seconds)
        evidence = await client.call(
            tool,
            str(self.target_path),
            arguments if arguments is not None else getattr(self, "arguments", {}) or {},
        )
        result = evidence.model_dump(mode="json")
        return Data(text=json.dumps(result, ensure_ascii=True), data=result)


class REATargetValidationComponent(ReaNodeComponent):
    display_name = "REA Target Validation"
    description = "Authorize a local target, open it in REA, and return the REA session identity."
    name = "REATargetValidation"
    icon = "ShieldCheck"
    inputs = [*_COMMON_INPUTS]
    outputs = [Output(display_name="Target Status", name="status", method="validate_target")]

    async def validate_target(self) -> Data:
        return await self._invoke_async("binary_session")


class REAAnalyzeComponent(ReaNodeComponent):
    display_name = "REA Analyze"
    description = "Run REA's binary overview analysis on an authorized target."
    name = "REAAnalyze"
    icon = "ScanSearch"
    inputs = [*_ANALYSIS_INPUTS]
    outputs = [Output(display_name="Analysis Evidence", name="evidence", method="analyze_target")]

    async def analyze_target(self) -> Data:
        return await self._invoke_async("binary_overview")


class REAInspectComponent(ReaNodeComponent):
    display_name = "REA Inspect"
    description = "Inspect a connected REA evidence record using a selected analysis view."
    name = "REAInspect"
    icon = "FileSearch"
    inputs = [*_ANALYSIS_INPUTS, JSONInput(name="source_evidence", display_name="Source REA Evidence", required=True)]
    outputs = [Output(display_name="Inspection Evidence", name="evidence", method="inspect_target")]

    async def inspect_target(self) -> Data:
        source = self.source_evidence
        if isinstance(source, Data):
            source = source.data
        if not isinstance(source, dict):
            raise ValueError("REA Inspect requires a connected REA evidence output.")
        source_evidence = source.get("structured_content")
        if not isinstance(source_evidence, dict):
            raise ValueError("Connected REA result does not contain structured Evidence.")
        arguments = dict(getattr(self, "arguments", {}) or {})
        arguments["source"] = {"kind": "inline", "evidence": source_evidence}
        return await self._invoke_async("inspect_analysis_view", arguments)


class REASearchSymbolsComponent(ReaNodeComponent):
    display_name = "REA Search Symbols / Procedures"
    description = "Search symbols and procedures in an authorized target."
    name = "REASearchSymbolsProcedures"
    icon = "ListFilter"
    inputs = [*_ANALYSIS_INPUTS]
    outputs = [Output(display_name="Search Evidence", name="evidence", method="search_target")]

    async def search_target(self) -> Data:
        return await self._invoke_async("search_procedures")


class READecompileComponent(ReaNodeComponent):
    display_name = "REA Decompile"
    description = "Request pseudocode for a selected procedure without executing target code."
    name = "READecompile"
    icon = "Braces"
    inputs = [*_ANALYSIS_INPUTS]
    outputs = [Output(display_name="Decompilation Evidence", name="evidence", method="decompile_target")]

    async def decompile_target(self) -> Data:
        return await self._invoke_async("procedure_pseudo_code")


class REACallGraphComponent(ReaNodeComponent):
    display_name = "REA Call Graph"
    description = "Retrieve REA's call graph for a selected procedure or address."
    name = "REACallGraph"
    icon = "Network"
    inputs = [*_ANALYSIS_INPUTS]
    outputs = [Output(display_name="Call Graph Evidence", name="evidence", method="build_call_graph")]

    async def build_call_graph(self) -> Data:
        return await self._invoke_async("get_call_graph")


class REACollectEvidenceComponent(Component):
    display_name = "REA Evidence Collection"
    description = "Collect explicit REA evidence outputs from this workflow."
    name = "REACollectEvidence"
    icon = "Archive"
    inputs = [
        JSONInput(name="analysis_evidence", display_name="Analysis Evidence"),
        JSONInput(name="inspection_evidence", display_name="Inspection Evidence"),
        JSONInput(name="search_evidence", display_name="Search Evidence"),
        JSONInput(name="decompilation_evidence", display_name="Decompilation Evidence"),
        JSONInput(name="call_graph_evidence", display_name="Call Graph Evidence"),
    ]
    outputs = [Output(display_name="Evidence Bundle", name="evidence", method="collect_evidence")]

    def collect_evidence(self) -> Data:
        records = []
        for field in (
            "analysis_evidence",
            "inspection_evidence",
            "search_evidence",
            "decompilation_evidence",
            "call_graph_evidence",
        ):
            item = getattr(self, field, None)
            if isinstance(item, Data):
                item = item.data
            if item is None:
                continue
            if not isinstance(item, dict):
                raise ValueError(f"{field} must contain a normalized REA evidence object.")
            records.append(item)
        if not records:
            raise ValueError("Connect at least one REA evidence output.")
        bundle = {"provider": "REA", "records": records}
        return Data(text=json.dumps(bundle, ensure_ascii=True), data=bundle)


class REAFindingsReportComponent(Component):
    display_name = "REA Findings / Report"
    description = "Separate source observations, hypotheses, and explicit unknowns without inventing evidence."
    name = "REAFindingsReport"
    icon = "ClipboardList"
    inputs = [
        StrInput(name="task_request", display_name="Investigation Question", required=True),
        JSONInput(name="evidence", display_name="REA Evidence", required=True),
    ]
    outputs = [Output(display_name="Findings Report", name="report", method="build_report")]

    def build_report(self) -> Data:
        evidence = self.evidence
        if isinstance(evidence, Data):
            evidence = evidence.data
        if not isinstance(evidence, dict):
            raise ValueError("REA Findings / Report requires an evidence object.")

        records = evidence.get("records", [evidence]) if isinstance(evidence, dict) else evidence
        if not isinstance(records, list) or not all(isinstance(record, dict) for record in records):
            raise ValueError("REA Findings / Report requires REA evidence records.")

        facts: list[Any] = []
        hypotheses: list[Any] = []
        unknowns: list[Any] = []
        limitations: list[Any] = []
        observations = []
        for record in records:
            observed = record.get("structured_content")
            result = observed.get("normalized_result") if isinstance(observed, dict) else None
            if isinstance(result, dict):
                for key, destination in (("facts", facts), ("hypotheses", hypotheses), ("unknowns", unknowns)):
                    values = result.get(key)
                    if isinstance(values, list):
                        destination.extend(values)
                    elif values is not None:
                        destination.append(values)
            if isinstance(observed, dict):
                limitations.extend(observed.get("limitations", []))
            observations.append(
                {
                    "tool": record.get("tool"),
                    "target_path": record.get("target_path"),
                    "observed_at": record.get("observed_at"),
                    "status": record.get("status"),
                    "normalized_result": result,
                }
            )
        report = {
            "request": self.task_request,
            "source": {"provider": "REA", "record_count": len(records)},
            "facts": facts,
            "hypotheses": hypotheses,
            "unknowns": unknowns,
            "limitations": limitations,
            "observations": observations,
            "evidence": records,
            "interpretation_policy": "Only REA-provided facts are classified as facts; no target code is executed.",
        }
        return Data(text=json.dumps(report, ensure_ascii=True), data=report)
