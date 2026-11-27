# Docling Bundle

Docling components for PrimeAgent packaged as a standalone Extension Bundle.

## Components

- Docling
- Docling Serve
- Export DoclingDocument
- Chunk DoclingDocument

## Install

The bundle is installed with PrimeAgent in the 1.10 workspace. The base package includes `docling-core` for the `DoclingDocument` schema. For standalone local conversion:

```bash
uv pip install "wfx-docling[local]"
```

Chunking and picture-description support use separate optional extras. Chunking
does not install the full local converter/OCR stack:

```bash
uv pip install "wfx-docling[chunking]"
uv pip install "wfx-docling[image-description]"
```

## Develop

```bash
uv run wfx extension validate src/bundles/docling/src/wfx_docling
uv run pytest src/bundles/docling/tests
```
