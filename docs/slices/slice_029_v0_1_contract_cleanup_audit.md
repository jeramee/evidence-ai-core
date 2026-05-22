# slice_029_v0_1_contract_cleanup_audit

## Current checkpoint

Project 1 is green through `slice_027_packet_inventory_jsonl_export`, with documentation/status aligned through `slice_028_readme_code_status_inventory_jsonl_update`.

Current validated bundle:

```text
129 passed
```

## Target

Record the v0.1 contract cleanup audit and make the feature stop-line visible in repository docs/status files.

## Why this is next

After inventory JSONL export, Project 1 has enough static/local packet mechanics for v0.1. The next work should freeze feature growth and verify that public API names, CLI names, JSON output contracts, artifact names, schema names, and error classes do not imply proof, validation authority, source-control mutation, adapter execution, or workflow ownership.

## Scope

This slice updates documentation/status only:

```text
README.md
CODE_STATUS.md
TEST_STATUS.md
docs/slices/slice_029_v0_1_contract_cleanup_audit.md
```

## Audit result

No production code rename is required before v0.1 freeze.

The current public API remains acceptable for v0.1 because the exported names are static/local packet mechanics:

- `create_static_packet()`
- `verify_packet()`
- `inspect_packet()`
- `load_packet()`
- `summarize_packet()`
- `read_artifact_manifest()`
- `summarize_artifact_hashes()`
- `list_schema_contracts()`
- `load_schema_contract()`
- `export_packet_zip()`
- `preview_packet_zip()`
- `extract_packet_zip()`
- `inventory_packet_bundle()`
- `export_packet_inventory_jsonl()`

The CLI names also remain acceptable for v0.1 because they describe thin local packet utilities:

- `create-static`
- `verify`
- `inspect`
- `summary`
- `manifest`
- `hash-summary`
- `schema-index`
- `schema-contract`
- `export-zip`
- `import-zip-preview`
- `import-zip-extract`
- `bundle-inventory`
- `bundle-inventory-jsonl`

The word `verify` remains mechanical-only in the docs and result contracts. It does not mean scientific validation, publication approval, replay proof, or promotion.

## Non-goals

This slice does not add production code behavior.

It does not add:

- txtai runtime calls,
- paperetl runtime calls,
- paperai runtime calls,
- Papermill execution,
- Quarto rendering,
- model calls,
- network calls,
- source-control mutation,
- validation authority,
- promotion authority,
- RunLab behavior,
- TraceLab behavior,
- adapter execution,
- workflow orchestration,
- background workers.

## Test posture

No new test is required for this documentation/status-only slice because no production code, tests, schemas, or CLI behavior changed.

The current validated bundle remains:

```text
129 passed
```

## Acceptance criteria

- README includes the v0.1 feature stop-line.
- CODE_STATUS records the v0.1 cleanup audit.
- TEST_STATUS is no longer stale and reflects the 129-test bundle.
- This slice document exists.
- No production code behavior changes are made.
- No new user-facing Project 1 feature is introduced.

## Stop-line

Stop after recording the cleanup audit. The next allowed v0.1 work is docs/examples alignment, packaging/release polish, public API stability notes, or release-candidate closeout.
