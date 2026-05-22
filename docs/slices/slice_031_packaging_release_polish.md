# slice_031_packaging_release_polish

## Current checkpoint

```text
slice_030_docs_examples_alignment
129 passed
```

## Exact next target

Record and validate v0.1 packaging release polish.

## Why it is next

After docs/examples alignment, the release-hardening lane needs to verify that the installable package preserves the CLI entry point and includes the static JSON Schema contracts needed by schema discovery.

## Scope

This slice is packaging/config plus targeted test coverage.

It adds package-data coverage for static schema contracts and mirrors the root `schemas/*.schema.json` files under `src/evidence_ai_core/schemas/` so installed package layouts can still discover schema contracts.

## Repo files involved

```text
pyproject.toml
src/evidence_ai_core/schema_index.py
src/evidence_ai_core/schemas/*.schema.json
tests/test_packaging.py
README.md
CODE_STATUS.md
TEST_STATUS.md
docs/slices/slice_031_packaging_release_polish.md
```

## Production/config changes

- `pyproject.toml` declares `evidence_ai_core = ["schemas/*.schema.json"]` package data.
- Root schema files are mirrored under `src/evidence_ai_core/schemas/`.
- Schema discovery now checks packaged schema data first, then source-tree schemas, then current-working-directory schemas.
- No new runtime dependency is added.

## Tests

Targeted test:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_packaging.py::test_pyproject_declares_cli_entry_point_and_schema_package_data
```

Bundle:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_core.py tests/test_schema_contract.py tests/test_cli.py tests/test_cli_json_output.py tests/test_no_external_actions.py tests/test_api_contract.py tests/test_verification_result_contract.py tests/test_packet_reader.py tests/test_packet_summary.py tests/test_manifest.py tests/test_schema_index.py tests/test_packet_export.py tests/test_packet_import.py tests/test_packet_zip_roundtrip.py tests/test_packet_inventory.py tests/test_packaging.py
```

Validated result:

```text
132 passed
```

## Acceptance criteria

- CLI entry point remains declared in `pyproject.toml`.
- Static schema contracts are included as package data.
- Package schema mirror matches root schema contracts.
- Schema discovery works from a working directory without a local `schemas/` folder.
- No external action, adapter, notebook, model, network, source-control, validation, or promotion behavior is introduced.

## Stop-line

This slice is release-hardening only. Do not add new user-facing Project 1 features.
