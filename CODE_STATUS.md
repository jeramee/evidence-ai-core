# Code status

Project: `evidence-ai-core`

Package: `evidence_ai_core`

CLI: `evidence-ai-core`

Current status: static/local packet core checkpoint through `slice_027_packet_inventory_jsonl_export`; documentation/status aligned through `slice_028_readme_code_status_inventory_jsonl_update`; v0.1 cleanup audit recorded in `slice_029_v0_1_contract_cleanup_audit`; examples/docs aligned through `slice_030_docs_examples_alignment`; packaging release polish recorded in `slice_031_packaging_release_polish`; public API stability notes recorded in `slice_032_public_api_stability_notes`; v0.1 release-candidate closeout recorded in `slice_033_v0_1_release_candidate_closeout`.

Current validated test bundle:

```text
132 passed
```

## Completed implementation slices

```text
slice_001_static_minimal_evidence_packet
slice_002_packet_verifier_hard_failures
slice_003_json_schema_minimum_contract
slice_004_cli_packet_smoke_hardening
slice_005_inspect_command_readonly_summary
slice_006_request_file_static_packet_input
slice_007_cli_failure_exit_codes_and_error_contract
slice_008_no_external_action_guardrails
slice_009_api_error_contract_and_public_exports
slice_010_verification_result_contract_hardening
slice_011_packet_reader_static_load_api
slice_012_packet_summary_api_or_cli_json_shape_hardening
slice_013_packet_manifest_reader_and_hash_summary
slice_014_schema_index_and_contract_discovery
slice_015_cli_json_output_stability_and_pretty_print_options
slice_016_readme_and_code_status_update
slice_017_static_packet_export_zip
slice_018_static_packet_import_zip_preview
slice_019_static_packet_import_extract_safe_mode
slice_020_readme_code_status_export_import_update
slice_021_static_packet_zip_roundtrip_contract
slice_022_readme_code_status_roundtrip_update
slice_023_static_packet_bundle_inventory
slice_024_readme_code_status_inventory_update
slice_025_packet_inventory_filter_and_sort_options
slice_026_readme_code_status_inventory_filter_sort_update
slice_027_packet_inventory_jsonl_export
```

## Completed documentation / release-hardening slices

```text
slice_028_readme_code_status_inventory_jsonl_update
slice_029_v0_1_contract_cleanup_audit
slice_030_docs_examples_alignment
slice_032_public_api_stability_notes
slice_033_v0_1_release_candidate_closeout
```

## Packaging release polish

`slice_031_packaging_release_polish` adds package-data coverage for the static JSON Schema contracts and confirms the CLI entry point remains declared in `pyproject.toml`.

Packaging behavior now includes:

- `pyproject.toml` declares `evidence-ai-core = "evidence_ai_core.cli:main"`.
- `pyproject.toml` includes `evidence_ai_core = ["schemas/*.schema.json"]` package data.
- Root schema files are mirrored under `src/evidence_ai_core/schemas/` for install/wheel use.
- Schema discovery prefers packaged schema data while preserving source-tree fallback behavior.
- No runtime adapter dependencies, model calls, network calls, notebook execution, source-control mutation, validation authority, or promotion authority were added.

## Public API stability notes

`slice_032_public_api_stability_notes` records the v0.1 public API stability posture in `docs/API_STABILITY.md` and README.

The documented public API is stable-ish for v0.1, not permanently frozen before v1.0. Documented functions, package-owned errors, CLI commands, compact JSON output shape, and static schema files should not change casually. Additive fields, compatibility aliases, packaging fixes, and authority-boundary corrections remain allowed before v1.0.

No production code behavior changed in this slice.


## v0.1 release-candidate closeout

`slice_033_v0_1_release_candidate_closeout` records the v0.1 release-candidate checklist, changelog draft, final test bundle command, and stop-line.

Release-candidate artifacts:

- `docs/RELEASE_CANDIDATE_CLOSEOUT.md`
- `CHANGELOG.md`
- `docs/slices/slice_033_v0_1_release_candidate_closeout.md`

Release-candidate status:

- Feature growth is stopped for v0.1.
- Current expected final bundle: `132 passed`.
- Project remains Project 1 only.
- No production code behavior changed in this closeout slice.
- No runtime integrations, adapters, model calls, network calls, notebook execution, source-control mutation, validation authority, or promotion authority were added.

## v0.1 feature stop-line

Project 1 is feature-complete for v0.1 after `slice_027_packet_inventory_jsonl_export`.

Until v0.1 release, work should stay limited to contract cleanup, public API stability notes, CLI/help-text stabilization, packaging polish, examples, README/docs alignment, and release-candidate closeout.

Do not add new user-facing packet features unless a blocker is discovered during cleanup/release review. Do not add txtai, paperetl, paperai, notebook execution, model calls, network calls, source-control mutation, RunLab behavior, TraceLab behavior, validation authority, promotion authority, adapter execution, orchestration, or workflow ownership.

## Contract cleanup audit result

The v0.1 contract cleanup audit found no required production-code rename before freeze.

Current public API names are mechanical/static-local and do not imply proof or promotion. Current CLI command names describe local packet utilities and do not imply notebook execution, model execution, source-control mutation, validation, or scientific truth. Current error classes remain package-owned and scoped to input, read, verification, export/import, and overwrite failures. Current schema files remain contract-bearing static JSON Schema definitions.

## Examples/docs alignment

The repository includes a static minimal example under `examples/static_minimal/` and a walkthrough in `docs/EXAMPLES.md`. The example documentation uses only local request/source files and read-only/mechanical CLI commands. It does not introduce runtime integrations, retrieval execution, notebook execution, validation authority, or promotion authority.

## Owns

- Static/local evidence packet creation.
- Required packet artifact contract.
- Conservative authority flags.
- Mechanical packet verification.
- Verification result contract.
- Public API exports.
- Package-owned error classes.
- CLI create/verify/inspect/summary/manifest/hash-summary/schema-index/schema-contract/export/import-preview/import-extract/bundle-inventory surfaces.
- Request-file static input.
- Read-only packet loading.
- Read-only packet summary.
- Artifact manifest reading.
- Artifact hash summary.
- Static schema index and schema contract discovery.
- Stable compact JSON output by default.
- Optional pretty JSON output.
- Static packet ZIP export.
- Preview-only packet ZIP import inspection.
- Safe packet ZIP extraction under an explicit output root.
- Static packet ZIP roundtrip contract tests.
- Static packet bundle inventory.
- Inventory filtering and deterministic sorting.
- Inventory JSONL export for filtered/sorted candidate lists.
- No-external-action guardrails.

## Does not own

- RunLab notebook execution.
- TraceLab/open-lab orchestration.
- Notebook UI.
- Papermill execution.
- Quarto rendering.
- `txtai` execution.
- `paperetl` execution.
- `paperai` execution.
- Model calls.
- Network calls.
- Background workers.
- External services.
- Source-control mutation.
- Scientific validation authority.
- Promotion authority.

## Current public API

```python
from evidence_ai_core import (
    EvidenceCoreError,
    PacketAlreadyExistsError,
    PacketExportError,
    PacketImportError,
    PacketInputError,
    PacketReadError,
    PacketVerificationError,
    create_static_packet,
    export_packet_zip,
    extract_packet_zip,
    export_packet_inventory_jsonl,
    inspect_packet,
    inventory_packet_bundle,
    list_schema_contracts,
    load_packet,
    load_schema_contract,
    preview_packet_zip,
    read_artifact_manifest,
    summarize_artifact_hashes,
    summarize_packet,
    verify_packet,
)
```

## Current CLI commands

```text
evidence-ai-core create-static
evidence-ai-core verify
evidence-ai-core inspect
evidence-ai-core summary
evidence-ai-core manifest
evidence-ai-core hash-summary
evidence-ai-core schema-index
evidence-ai-core schema-contract
evidence-ai-core export-zip
evidence-ai-core import-zip-preview
evidence-ai-core import-zip-extract
evidence-ai-core bundle-inventory
evidence-ai-core bundle-inventory-jsonl
```

## Current inventory options

```text
bundle-inventory --kind all|dirs|zips
bundle-inventory --status all|passed|failed
bundle-inventory --sort relative-path|name|kind|verification-status
bundle-inventory --reverse
bundle-inventory-jsonl --output-jsonl <path>
bundle-inventory-jsonl --overwrite
```

## Test command

```powershell
Set-Location "C:\temp_coding\000_CodingTools\000_ProductLine\evidence-ai-core"

.\.venv\Scripts\python.exe -m pytest -q tests/test_core.py tests/test_schema_contract.py tests/test_cli.py tests/test_cli_json_output.py tests/test_no_external_actions.py tests/test_api_contract.py tests/test_verification_result_contract.py tests/test_packet_reader.py tests/test_packet_summary.py tests/test_manifest.py tests/test_schema_index.py tests/test_packet_export.py tests/test_packet_import.py tests/test_packet_zip_roundtrip.py tests/test_packet_inventory.py tests/test_packaging.py
```

Expected result:

```text
132 passed
```

## Boundary note

The central rule remains:

> Evidence is not proof.

Mechanical packet verification, schema discovery, manifest summaries, hash summaries, ZIP export, ZIP preview, ZIP extraction, ZIP roundtrip contracts, bundle inventory, and inventory JSONL export are evidence mechanics only. They are not scientific validation, approval, replay proof, source-control settlement, or promotion.
