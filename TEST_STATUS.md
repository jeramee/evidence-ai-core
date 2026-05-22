# Test status

Current validated Project 1 bundle:

```powershell
Set-Location "C:\temp_coding\000_CodingTools\000_ProductLine\evidence-ai-core"

.\.venv\Scripts\python.exe -m pytest -q tests/test_core.py tests/test_schema_contract.py tests/test_cli.py tests/test_cli_json_output.py tests/test_no_external_actions.py tests/test_api_contract.py tests/test_verification_result_contract.py tests/test_packet_reader.py tests/test_packet_summary.py tests/test_manifest.py tests/test_schema_index.py tests/test_packet_export.py tests/test_packet_import.py tests/test_packet_zip_roundtrip.py tests/test_packet_inventory.py tests/test_packaging.py
```

Expected current result:

```text
132 passed
```

## Scope

This test status belongs to Project 1 only: `evidence-ai-core`.

The current green bundle covers static/local packet creation, mechanical verification, schema contract discovery, CLI JSON output, no-external-action guardrails, public API/error contract, packet reading and summary, manifest/hash summary, schema index, static ZIP export/import/roundtrip, bundle inventory, filter/sort options, and inventory JSONL export, and packaging release polish.

It does not validate RunLab, TraceLab, notebook execution, model execution, retrieval execution, scientific correctness, source-control settlement, or promotion authority.


## Documentation-only release-hardening note

`slice_032_public_api_stability_notes` is documentation-only. It records public API stability posture and does not change production code, tests, schemas, CLI behavior, package metadata, or package data. The current green bundle remains:

```text
132 passed
```

## v0.1 release-candidate closeout validation

`slice_033_v0_1_release_candidate_closeout` is a release-candidate documentation/status slice. It records the final checklist and changelog draft, and it uses the same full Project 1 validation bundle.

Expected release-candidate result:

```text
132 passed
```

This closeout still belongs to Project 1 only. It does not validate RunLab, TraceLab, notebook execution, model execution, retrieval execution, scientific correctness, source-control settlement, or promotion authority.
