# slice_028_readme_code_status_inventory_jsonl_update

## Current checkpoint

`evidence-ai-core` is implemented and locally validated through:

```text
slice_027_packet_inventory_jsonl_export
129 passed
```

## Exact next target

Align README and CODE_STATUS with the already-implemented inventory JSONL export surface.

## Why it is next

The code and tests already include `export_packet_inventory_jsonl()` and the `evidence-ai-core bundle-inventory-jsonl` CLI command, but README and CODE_STATUS were still describing the checkpoint as complete only through `slice_025_packet_inventory_filter_and_sort_options` with `123 passed`.

This slice is documentation/status alignment only.

## Scope

Update documentation to mention:

- `export_packet_inventory_jsonl()` public API.
- `evidence-ai-core bundle-inventory-jsonl` CLI command.
- JSONL output behavior: one compact sorted JSON object per filtered/sorted inventory candidate.
- JSONL export result fields such as candidate count, JSONL record count, output path, bytes written, filters, sort options, authority flags, and limitations.
- Current checkpoint through `slice_027_packet_inventory_jsonl_export`.
- Current validated bundle result: `129 passed`.

## Non-goals

This slice does not change production code, packet contracts, CLI behavior, tests, schemas, import/export mechanics, inventory mechanics, packaging metadata, or runtime behavior.

It does not add txtai, paperetl, paperai, notebook execution, model calls, network calls, source-control mutation, RunLab behavior, TraceLab behavior, scientific validation authority, or promotion authority.

## Repo file(s) involved

```text
README.md
CODE_STATUS.md
docs/slices/slice_028_readme_code_status_inventory_jsonl_update.md
```

## Expected API behavior

No API behavior change.

The already-implemented API remains:

```python
from evidence_ai_core import export_packet_inventory_jsonl
```

## Expected CLI behavior

No CLI behavior change.

The already-implemented command remains:

```powershell
evidence-ai-core bundle-inventory-jsonl .\packets --output-jsonl .\inventory.jsonl
```

## Data/artifact contract changes

None.

## Exact implementation summary

README now documents the JSONL export API and CLI surface.

CODE_STATUS now reports the implementation lane through `slice_027_packet_inventory_jsonl_export` and `129 passed`.

## Exact tests

No test is required for this documentation/status-only slice.

The pre-existing implementation bundle was inspected and remains the relevant validation signal:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_core.py tests/test_schema_contract.py tests/test_cli.py tests/test_cli_json_output.py tests/test_no_external_actions.py tests/test_api_contract.py tests/test_verification_result_contract.py tests/test_packet_reader.py tests/test_packet_summary.py tests/test_manifest.py tests/test_schema_index.py tests/test_packet_export.py tests/test_packet_import.py tests/test_packet_zip_roundtrip.py tests/test_packet_inventory.py
```

Expected result:

```text
129 passed
```

## Acceptance criteria

- README mentions `export_packet_inventory_jsonl()`.
- README mentions `evidence-ai-core bundle-inventory-jsonl`.
- README documents output JSONL behavior.
- README preserves the evidence-is-not-proof boundary.
- CODE_STATUS reflects completion through `slice_027_packet_inventory_jsonl_export`.
- CODE_STATUS reports `129 passed`.
- This slice document exists.
- No production code behavior changes are made.

## Stop-line

Stop after documentation/status alignment. Do not add new user-facing Project 1 features before v0.1 freeze planning unless a blocker is discovered.
