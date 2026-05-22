# v0.1 release-candidate closeout

Project: `evidence-ai-core`

Release lane: v0.1 release candidate

Core rule:

> Evidence is not proof.

## Current checkpoint

```text
slice_033_v0_1_release_candidate_closeout
132 passed
```

## Release-candidate decision

`evidence-ai-core` is feature-complete for v0.1 after `slice_027_packet_inventory_jsonl_export`.

The v0.1 release-candidate lane is now limited to final review, source-control settlement, tag/release preparation, and any blocker fixes discovered during release review.

Do not add new user-facing packet features before v0.1 release.

## Final Project 1 validation bundle

```powershell
Set-Location "C:\temp_coding\000_CodingTools\000_ProductLine\evidence-ai-core"

.\.venv\Scripts\python.exe -m pytest -q tests/test_core.py tests/test_schema_contract.py tests/test_cli.py tests/test_cli_json_output.py tests/test_no_external_actions.py tests/test_api_contract.py tests/test_verification_result_contract.py tests/test_packet_reader.py tests/test_packet_summary.py tests/test_manifest.py tests/test_schema_index.py tests/test_packet_export.py tests/test_packet_import.py tests/test_packet_zip_roundtrip.py tests/test_packet_inventory.py tests/test_packaging.py
```

Expected result:

```text
132 passed
```

## Release-candidate checklist

- [x] Static/local packet creation is implemented.
- [x] Mechanical verifier hard failures are implemented.
- [x] Minimum static JSON Schema contracts are present.
- [x] CLI create/verify/inspect/summary/manifest/hash-summary/schema-index/schema-contract/export/import/inventory surfaces are implemented.
- [x] Stable compact/pretty JSON CLI output is tested.
- [x] Public API and package-owned errors are documented.
- [x] Read-only packet loading and packet summary APIs are implemented.
- [x] Manifest and artifact hash summary APIs are implemented.
- [x] Static schema discovery is implemented.
- [x] Static ZIP export/import/roundtrip mechanics are implemented.
- [x] Bundle inventory, filter/sort options, and JSONL export are implemented.
- [x] No-external-action guardrails are tested.
- [x] README and CODE_STATUS are aligned.
- [x] TEST_STATUS records the current full bundle.
- [x] Static minimal example docs are aligned.
- [x] Packaged schema data is included for install/wheel use.
- [x] Public API stability notes are recorded.
- [x] Changelog draft exists.
- [x] v0.1 feature stop-line is visible.

## Boundary checklist

The release candidate does not add:

- notebook execution,
- Papermill execution,
- Quarto rendering,
- `txtai` execution,
- `paperetl` execution,
- `paperai` execution,
- model calls,
- network calls,
- source-control mutation,
- RunLab behavior,
- TraceLab behavior,
- lab/instrument orchestration,
- scientific validation authority,
- promotion authority,
- adapter execution,
- workflow ownership.

## Release-candidate artifacts

```text
README.md
CODE_STATUS.md
TEST_STATUS.md
CHANGELOG.md
docs/API_STABILITY.md
docs/EXAMPLES.md
docs/RELEASE_CANDIDATE_CLOSEOUT.md
docs/slices/slice_033_v0_1_release_candidate_closeout.md
examples/static_minimal/README.md
pyproject.toml
src/evidence_ai_core/schemas/*.schema.json
```

## Stop-line

Stop after release-candidate closeout.

Only fix blockers discovered during release review. Do not add new Project 1 features before v0.1 release.
