# Dependency audit

## High-cost feature dependencies

- `@xyflow/react`, `reactflow`, and `elkjs`: graph editor and layout. Keep behind the flow route.
- `react-markdown`, `react-syntax-highlighter`, `rehype-*`, and `remark-*`: markdown/chat rendering. Keep out of the shell and isolate code blocks.
- `ace-builds`, `react-ace`, and `vanilla-jsoneditor`: editors. Load only from editor surfaces.
- `ag-grid-community` and `ag-grid-react`: large tables. Prefer their built-in row virtualization and avoid mounting hidden grids.
- `react-pdf` and `openseadragon`: document/media surfaces. Load on demand.
- `framer-motion`: use feature loading or CSS transitions for simple opacity/transform effects.

## Duplicates and follow-up

The repository currently contains both `reactflow` and `@xyflow/react`, plus both `moment` and `date-fns`. This audit does not remove them because usage and compatibility need a separate dependency migration. Search import sites before consolidating.

No dependency versions were changed by the performance pass.
