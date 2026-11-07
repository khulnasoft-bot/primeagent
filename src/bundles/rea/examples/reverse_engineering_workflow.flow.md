# Authorized Target Investigation

Submit the following compact spec to `create_flow_from_spec` through the
existing `wfx-mcp` server. Replace `/srv/authorized-targets/example.bin` with
an existing file under `REA_ALLOWED_TARGET_ROOTS` and choose procedure
selectors appropriate to the target.

```text
name: Authorized REA Investigation
description: Validate one target, inspect it, search and decompile a selected procedure, then report evidence.

nodes:
  request: ChatInput
  validate: ext:rea:REATargetValidationComponent@official
  analyze: ext:rea:REAAnalyzeComponent@official
  inspect: ext:rea:REAInspectComponent@official
  search: ext:rea:REASearchSymbolsComponent@official
  decompile: ext:rea:READecompileComponent@official
  collect: ext:rea:REACollectEvidenceComponent@official
  report: ext:rea:REAFindingsReportComponent@official
  output: ChatOutput

edges:
  validate.status -> analyze.validation
  validate.status -> inspect.validation
  validate.status -> search.validation
  validate.status -> decompile.validation
  analyze.evidence -> inspect.source_evidence
  analyze.evidence -> collect.analysis_evidence
  inspect.evidence -> collect.inspection_evidence
  search.evidence -> collect.search_evidence
  decompile.evidence -> collect.decompilation_evidence
  collect.evidence -> report.evidence
  request.message -> report.task_request
  report.report -> output.input_value

config:
  validate.target_path: /srv/authorized-targets/example.bin
  analyze.target_path: /srv/authorized-targets/example.bin
  inspect.target_path: /srv/authorized-targets/example.bin
  inspect.arguments: {"view":{"kind":"summary"}}
  search.target_path: /srv/authorized-targets/example.bin
  search.arguments: {"pattern":"auth","mode":"literal"}
  decompile.target_path: /srv/authorized-targets/example.bin
  decompile.arguments: {"procedure":"main"}
```

Every analysis node independently rechecks the allowed root and opens the
target in its own short-lived REA session. Evidence moves between nodes as
explicit WFX data. The report is intentionally evidence-only: use PrimeAgent's
existing Agent component to plan an implementation from the report, and keep
implementation, code execution, and verification behind the project's normal
review and approval steps.