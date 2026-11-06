import pytest
from wfx_rea.components.rea import (
    REAAnalyzeComponent,
    REACallGraphComponent,
    REACollectEvidenceComponent,
    READecompileComponent,
    REAFindingsReportComponent,
    REAInspectComponent,
    REASearchSymbolsComponent,
    REATargetValidationComponent,
)

_ANALYSIS_NODES = [
    REAAnalyzeComponent,
    REAInspectComponent,
    REASearchSymbolsComponent,
    READecompileComponent,
    REACallGraphComponent,
]


def test_rea_nodes_are_exported_with_unique_component_names():
    nodes = [
        REATargetValidationComponent,
        *_ANALYSIS_NODES,
        REACollectEvidenceComponent,
        REAFindingsReportComponent,
    ]

    assert len({node.name for node in nodes}) == 8
    assert all(node.outputs for node in nodes)
    assert all(callable(getattr(node, output.method, None)) for node in nodes for output in node.outputs)


@pytest.mark.parametrize("node", _ANALYSIS_NODES)
def test_investigation_nodes_require_successful_target_validation(node):
    input_names = {item.name for item in node.inputs}

    required_inputs = {"target_path", "validation", "arguments", "timeout_seconds"}
    if node is REAInspectComponent:
        required_inputs.add("source_evidence")
    assert required_inputs <= input_names


def test_evidence_collection_accepts_explicit_cross_node_records():
    input_names = {item.name for item in REACollectEvidenceComponent.inputs}

    assert input_names == {
        "analysis_evidence",
        "inspection_evidence",
        "search_evidence",
        "decompilation_evidence",
        "call_graph_evidence",
    }
