# Code status

Project: `evidence-ai-core`

Package: `evidence_ai_core`

CLI: `evidence-ai-core`

Current status: static/local packet core checkpoint through `slice_025_packet_inventory_filter_and_sort_options`.

Current validated test bundle:

```text
123 passed
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
```

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
```

## Current inventory options

```text
bundle-inventory --kind all|dirs|zips
bundle-inventory --status all|passed|failed
bundle-inventory --sort relative-path|name|kind|verification-status
bundle-inventory --reverse
```

## Test command

```powershell
Set-Location "C:\temp_coding\000_CodingTools\000_ProductLine\evidence-ai-core"

.\.venv\Scripts\python.exe -m pytest -q tests/test_core.py tests/test_schema_contract.py tests/test_cli.py tests/test_cli_json_output.py tests/test_no_external_actions.py tests/test_api_contract.py tests/test_verification_result_contract.py tests/test_packet_reader.py tests/test_packet_summary.py tests/test_manifest.py tests/test_schema_index.py tests/test_packet_export.py tests/test_packet_import.py tests/test_packet_zip_roundtrip.py tests/test_packet_inventory.py
```

Expected result:

```text
123 passed
```

## Boundary note

The central rule remains:

> Evidence is not proof.

Mechanical packet verification, schema discovery, manifest summaries, hash summaries, ZIP export, ZIP preview, ZIP extraction, ZIP roundtrip contracts, and bundle inventory are evidence mechanics only. They are not scientific validation, approval, replay proof, source-control settlement, or promotion.
