# slice_020_readme_code_status_export_import_update

## Current checkpoint

`slice_019_static_packet_import_extract_safe_mode` is green.

Current validated bundle:

```text
105 passed
```

## Target

Update repository documentation to match the implemented static/local packet core through slice 019, including ZIP export, ZIP import preview, and safe ZIP extraction.

## Files updated

```text
README.md
CODE_STATUS.md
docs/slices/slice_020_readme_code_status_export_import_update.md
```

## Scope

This is a documentation/status checkpoint only.

It records the implemented code surface:

- static packet creation,
- verifier hard failures,
- JSON Schema minimum contracts,
- CLI smoke behavior,
- inspect summary,
- request-file input,
- CLI exit behavior,
- no-external-action guardrails,
- public API and errors,
- verification result contract,
- packet reader API,
- packet summary API/CLI,
- manifest reader and hash summary,
- schema index and contract discovery,
- stable compact/pretty CLI JSON output,
- static packet ZIP export,
- preview-only packet ZIP import inspection,
- safe packet ZIP extraction.

## Non-goals

This slice does not add code behavior.

It does not add:

- adapters,
- model calls,
- network calls,
- notebook execution,
- `txtai` execution,
- `paperetl` execution,
- `paperai` execution,
- source-control mutation,
- scientific validation authority,
- promotion authority.

## Test posture

No new test is required for this documentation-only slice because the prior implementation checkpoint is already green.

Current code checkpoint remains:

```text
105 passed
```

## Acceptance criteria

- README describes the actual implemented Project 1 surface through slice 019.
- CODE_STATUS reflects slices 001 through 019.
- Documentation preserves the boundary: evidence is not proof.
- Documentation does not imply RunLab, TraceLab, notebook execution, adapter execution, validation, or promotion ownership.
