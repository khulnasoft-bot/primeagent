# wfx-rea

`wfx-rea` adds evidence-driven reverse-engineering nodes to PrimeAgent WFX. It
connects to REA through the existing stdio MCP server and uses REA's CLI only
for operations with documented one-shot commands.

## Install

For a source checkout, install the bundle into the environment that already
contains WFX with `uv pip install --no-deps -e src/bundles/rea`. For a
standalone WFX deployment, install the published `wfx-rea` package after it is
released. Install REA separately and configure its provider tools before
running a workflow.

Set an explicit analysis boundary in the WFX process environment:

```bash
export REA_ALLOWED_TARGET_ROOTS=/srv/authorized-targets
export REA_MAX_TARGET_BYTES=2147483648
export REA_MCP_COMMAND=rea
export REA_MCP_ARGS='["mcp"]'
export REA_CLI_COMMAND=rea
export REA_SUBPROCESS_ENV_ALLOWLIST=MY_REA_PROVIDER_TOKEN
```

Multiple allowed roots are separated by the platform path separator. Target
paths are resolved before checking containment, so a symlink cannot escape an
authorized root. The default REA MCP command uses an already-installed `rea`
executable; the workflow never downloads or updates REA at runtime.
Only runtime essentials and `REA_` / analysis-provider-prefixed variables are
inherited by REA. Add other required variable names explicitly to
`REA_SUBPROCESS_ENV_ALLOWLIST`; unrelated PrimeAgent credentials are not
forwarded.

## Nodes

The extension registers these namespaced components under the `rea` bundle:

* `REATargetValidationComponent` opens the authorized local target and returns
  REA's session status. Connect this output to the required `validation` input
  on every analysis node.
* `REAAnalyzeComponent` requests `binary_overview`.
* `REAInspectComponent` requests `inspect_analysis_view`.
* `REASearchSymbolsComponent` requests `search_procedures`.
* `READecompileComponent` requests `procedure_pseudo_code`.
* `REACallGraphComponent` requests `get_call_graph`.
* `REACollectEvidenceComponent` collects explicit evidence outputs from other
  WFX nodes. REA evidence is process-session scoped, so this node does not
  assume a later connection can retrieve an earlier process's in-memory bundle.
* `REAFindingsReportComponent` preserves source observations and separately
  forwards REA-provided facts, hypotheses, unknowns, and limitations.

Analysis nodes use a fresh, bounded REA process for each call and close it on
success, timeout, failure, or cancellation. The CLI fallback supports target
status/overview, procedure search and decompilation, analysis-view inspection,
and evidence-bundle inspection. Call graph operations require MCP.

See [`examples/reverse_engineering_workflow.flow.md`](examples/reverse_engineering_workflow.flow.md)
for a flow-spec example that can be submitted to `wfx-mcp`'s
`create_flow_from_spec` tool.

## Security Policy

This bundle fails closed unless `REA_ALLOWED_TARGET_ROOTS` is configured. It
accepts only existing local files or directories under those roots, limits
single-file size, and applies a per-operation timeout and response-size cap.
No analysis node exposes arbitrary MCP tool names. The adapter allows only
read-only REA operations and never executes recovered target code. Mutating,
debugger, instrumentation, extraction, and target-launch operations are not
exposed. CLI commands are invoked without a shell; cancellation kills the
owned process group on POSIX and reaps the process.

REA and its analysis providers are separate operator-installed software. Verify
their source and configuration, and authorize only targets you are permitted to
analyze. Analysis evidence is returned in WFX output; persistence is the
responsibility of downstream workflow nodes or PrimeAgent's configured
artifact storage. Do not treat reverse-engineered pseudocode as source-equivalent
or execute it without a separate review and explicit approval.

## Develop and Test

From the repository root:

```bash
uv run wfx extension validate src/bundles/rea/src/wfx_rea
uv run pytest src/bundles/rea/tests -q
```

The MCP tests use a controlled in-memory transport fixture; no real target or
REA provider is required.