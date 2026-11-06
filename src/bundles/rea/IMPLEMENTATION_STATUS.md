# REA WFX Integration Status

This checklist records the implementation boundary and acceptance criteria for the REA extension. A checked item means code is present; it does not imply tests passed when the environment could not run them.

## Phase 0: Architecture

- [x] WFX components are the workflow node abstraction; their declared output methods execute through `Component._get_output_result`.
- [x] WFX extension manifests and `primeagent.extensions` entry points are the registration mechanism.
- [x] `wfx-mcp` builds and executes PrimeAgent flows; REA's stdio MCP is a separate child process called by the extension adapter.
- [x] REA evidence is returned as explicit WFX data because REA session evidence is process-scoped.

## Phase 1: REA Integration Foundation

Acceptance criteria:

- [x] Use the documented REA stdio `mcp` command and discover supported tools from the live catalog.
- [x] Keep CLI fallback to documented one-shot commands and reject unsupported operations.
- [x] Validate and bound local target paths; preserve REA structured content, text content, server identity, target path, and observation time.
- [x] Bound calls and outputs; clean up on success, failure, timeout, and cancellation.
- [x] Fail closed unless allowed roots are configured; prevent local evidence-view references from escaping those roots.
- [x] Pass only runtime/provider variables and explicitly allowlisted environment variables into REA.
- [ ] Execute MCP and CLI fixture tests in a Python environment with pytest and the WFX/MCP dependencies installed.

## Phase 2: WFX Nodes

Acceptance criteria:

- [x] Export target validation, analysis, inspection, procedure search, decompilation, call graph, evidence collection, and findings/report nodes.
- [x] Require successful target-validation output on investigative nodes and retain evidence as normal WFX data outputs.
- [x] Provide a serializable flow spec using the existing `create_flow_from_spec` format.
- [ ] Run `wfx extension validate` and the node/flow-spec tests in an installed WFX environment.

## Phase 3: PrimeAgent Intelligence

Acceptance criteria:

- [x] Preserve source observations and separately expose REA-provided facts, hypotheses, unknowns, and limitations when present.
- [x] Permit explicit follow-up investigation by wiring evidence into REA Inspect or other investigation nodes.
- [ ] Add an Agent-backed plan node and automatic follow-up selection from unresolved questions.
- [ ] Add parallel sub-agent investigation orchestration using a verified PrimeAgent API.

## Phase 4: Analysis to Implementation

Acceptance criteria:

- [x] Demonstrate authorized validation, analysis, evidence collection, reconstruction findings, and report delivery in the example flow.
- [x] Document that implementation and verification should use existing PrimeAgent nodes and approval controls.
- [ ] Add a concrete implementation-planning stage, implementation stage, and test/verification stage to an executable example using verified component contracts.
- [ ] Add end-to-end execution tests for the complete analysis-to-implementation workflow.

## Phase 5: Hardening and Documentation

Acceptance criteria:

- [x] Document authorization roots, execution limits, transport configuration, evidence behavior, and the no-target-execution policy.
- [x] Add unit and controlled-fixture test cases for authorization, normalization, capability discovery, CLI mapping, partial results, timeout, cancellation, and node contracts.
- [ ] Run the new tests and relevant WFX regression tests.
- [ ] Run package build and manifest validation in the repository's full dependency environment.

## Current Blockers

- This container has no `pytest`, `pytest-asyncio`, Typer, or installed WFX command. The source WFX validator also cannot import because its runtime dependencies are absent.
- Offline lock resolution is blocked by an uncached pre-existing optional `clickhouse-connect` dependency; online resolution timed out fetching unrelated platform metadata. The integration therefore remains an independent bundle and does not modify the root workspace lock.
- The current implementation stops at evidence-backed reporting. It does not automatically generate code, run recovered code, make implementation changes, or invoke parallel agents.
