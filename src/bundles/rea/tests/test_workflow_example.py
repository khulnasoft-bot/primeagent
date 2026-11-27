from pathlib import Path

from wfx.graph.flow_builder.spec import parse_flow_spec, validate_spec_references


def test_documented_workflow_spec_parses_and_references_valid_nodes():
    example = Path(__file__).parents[1] / "examples" / "reverse_engineering_workflow.flow.md"
    document = example.read_text(encoding="utf-8")
    spec = document.split("```text\n", 1)[1].split("\n```", 1)[0]

    parsed = parse_flow_spec(spec)
    validate_spec_references(parsed)

    assert len(parsed["nodes"]) == 9
    assert {edge["target_input"] for edge in parsed["edges"] if edge["target_id"] == "analyze"} == {"validation"}
