# Changelog

## v0.1.0-rc.1 - draft

### Status

`evidence-ai-core` is a static/local evidence packet core for reproducible scientific RAG and AI-assisted research workflows.

Core rule:

> Evidence is not proof.

### Implemented

- Static/local packet creation.
- Mechanical packet verification.
- Minimum JSON Schema contracts.
- CLI create/verify/inspect/summary/manifest/hash-summary/schema-index/schema-contract/export/import/inventory surfaces.
- Stable compact and pretty JSON CLI output.
- Public API and package-owned error contract.
- Read-only packet loader and compact packet summary.
- Artifact manifest reader and artifact hash summary.
- Static schema index and schema contract discovery.
- Static packet ZIP export.
- Preview-only ZIP import inspection.
- Safe static packet ZIP extraction.
- Static ZIP roundtrip contract tests.
- Local packet bundle inventory.
- Inventory kind/status filtering.
- Deterministic inventory sorting.
- Inventory JSONL export.
- Packaged static schema data for install/wheel use.
- Static minimal example documentation.
- Public API stability notes.
- v0.1 release-candidate closeout checklist.

### Validation

Current expected Project 1 bundle:

```text
132 passed
```

### Boundaries

This release candidate does not include notebook execution, model calls, retrieval execution, `txtai`, `paperetl`, `paperai`, source-control mutation, RunLab behavior, TraceLab behavior, scientific validation authority, promotion authority, adapter execution, or workflow orchestration.
