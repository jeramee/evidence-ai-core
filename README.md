# evidence-ai-core

Static/local evidence packet core for reproducible scientific RAG and AI-assisted research workflows.

Core rule:

> Evidence is not proof.

`evidence-ai-core` creates, reads, summarizes, verifies, exports, previews, safely imports, roundtrip-checks, and inventories local evidence packets. It is a low-level packet and contract layer. It does **not** execute notebooks, call models, run retrieval systems, mutate source control, promote state, or validate scientific truth.

## v0.1 feature stop-line

`evidence-ai-core` is feature-complete for v0.1 after `slice_027_packet_inventory_jsonl_export`. The remaining v0.1 lane is release hardening: contract cleanup, public API stability notes, CLI/help-text stabilization, packaging polish, examples, README/docs alignment, and release-candidate closeout.

No new user-facing Project 1 packet features should be added before v0.1 unless cleanup/release review finds a blocker. Runtime adapters, notebooks, model calls, retrieval execution, source-control mutation, validation authority, promotion authority, RunLab behavior, and TraceLab behavior belong outside Project 1.

## Project identity

| Field | Value |
|---|---|
| Repo | `evidence-ai-core` |
| Python package | `evidence_ai_core` |
| CLI | `evidence-ai-core` |
| Product role | Low-level evidence packet core |
| Boundary | Static/local packet creation, reading, summaries, schemas, manifests, ZIP export/import mechanics, ZIP roundtrip contracts, bundle inventory/filtering/sorting, and mechanical checks |

## What this package owns

- Static/local evidence packet creation.
- The minimum evidence packet artifact set.
- Conservative authority flags.
- Mechanical packet verification.
- Static JSON Schema contract discovery.
- Read-only packet loading.
- Read-only packet summaries.
- Manifest and artifact hash summaries.
- Stable CLI JSON output.
- Static packet ZIP export.
- Preview-only packet ZIP import inspection.
- Safe packet ZIP extraction under an explicit output root.
- Static packet ZIP roundtrip contract tests.
- Static packet bundle inventory for local packet folders and packet ZIPs.
- Inventory filtering by candidate kind and status.
- Deterministic inventory sorting.
- Inventory JSONL export for filtered/sorted candidate lists.
- Stable package-owned error classes.
- Packaged static schema data for install/wheel use.

## What this package does not own

- Notebook execution.
- Papermill execution.
- Quarto rendering.
- `txtai` execution.
- `paperetl` execution.
- `paperai` execution.
- Model calls.
- Network calls.
- Source-control mutation.
- RunLab behavior.
- TraceLab behavior.
- Lab/instrument orchestration.
- Scientific validation.
- Promotion authority.

Higher-level products may use this package later, but this package remains the static evidence-packet core.

## Packaging / release posture

The package declares the `evidence-ai-core` CLI entry point in `pyproject.toml` and includes the static JSON Schema contracts as package data under `src/evidence_ai_core/schemas/`.

Schema discovery first checks the packaged schema data, then the source-tree `schemas/` directory, then a current-working-directory `schemas/` directory. This keeps schema discovery usable from an installed package while preserving source-tree development behavior.

## v0.1 release candidate closeout

`slice_033_v0_1_release_candidate_closeout` records the v0.1 release-candidate stop-line.

Current release-candidate posture:

- Project 1 is feature-complete for v0.1.
- Final release-candidate bundle target is `132 passed`.
- Public API stability notes are documented in `docs/API_STABILITY.md`.
- Static examples are documented in `docs/EXAMPLES.md` and `examples/static_minimal/`.
- Release checklist is documented in `docs/RELEASE_CANDIDATE_CLOSEOUT.md`.
- Changelog draft is documented in `CHANGELOG.md`.

This closeout does not add new packet features, adapters, notebook execution, model calls, retrieval execution, source-control mutation, scientific validation authority, or promotion authority.

## Static minimal example

A small local example is included under:

```text
examples/static_minimal/
```

The example contains a request file and one static source file:

```text
examples/static_minimal/inputs/request.txt
examples/static_minimal/inputs/source_a.md
```

Create a packet from the example inputs:

```powershell
evidence-ai-core create-static --request-file .\examples\static_minimal\inputs\request.txt --source .\examples\static_minimal\inputs\source_a.md --output-root .\examples\static_minimal\packets
```

Then run read-only/mechanical checks against the created packet directory:

```powershell
evidence-ai-core verify .\examples\static_minimal\packets\<packet_id>
evidence-ai-core summary .\examples\static_minimal\packets\<packet_id>
evidence-ai-core hash-summary .\examples\static_minimal\packets\<packet_id>
```

The example is intentionally static/local. It does not execute notebooks, call models, run retrieval, contact networks, mutate source control, validate scientific claims, or promote state.

## Required packet artifacts

A static packet contains these required artifacts:

```text
query_job.json
retrieval_record.json
source_citations.json
context_pack.md
notebook_run_record.json
environment_report.json
artifact_manifest.json
replay_manifest.json
```

These records describe what was requested, what placeholder retrieval/citation/context artifacts exist, what execution placeholder exists, what environment metadata was captured, what artifacts exist, and what replay limitations apply.

The current packet is intentionally conservative. It records evidence mechanics; it does not prove correctness.

## Authority flags

Default authority flags remain false:

```json
{
  "correctness_proven": false,
  "repo_mutated": false,
  "state_promoted": false,
  "source_control_touched": false
}
```

The verifier fails if a packet escalates these flags.

## Public Python API

```python
from evidence_ai_core import (
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

### Packet creation

```python
from pathlib import Path
from evidence_ai_core import create_static_packet

packet_dir = create_static_packet(
    request_text="What evidence supports this research claim?",
    source_paths=[Path("source.md")],
    output_root=Path("packets"),
)
```

### Mechanical verification

```python
from evidence_ai_core import verify_packet

result = verify_packet(packet_dir)
print(result["verification_status"])
```

Mechanical verification checks packet shape and artifact mechanics only.

It can fail for:

- missing required artifact,
- invalid JSON,
- missing required field,
- packet ID mismatch,
- artifact hash mismatch,
- forbidden authority escalation.

### Read-only packet loading

```python
from evidence_ai_core import load_packet

packet = load_packet(packet_dir)
print(packet["json_records"].keys())
```

`load_packet()` reads packet contents into one static structure. It does not repair, execute, validate, promote, or mutate anything.

### Compact packet summary

```python
from evidence_ai_core import summarize_packet

summary = summarize_packet(packet_dir)
print(summary["record_type"])
```

`summarize_packet()` returns compact packet status without embedding all JSON records or text artifacts.

### Manifest and hash summary

```python
from evidence_ai_core import summarize_artifact_hashes

hash_summary = summarize_artifact_hashes(packet_dir)
print(hash_summary["hash_status"])
```

This recomputes local SHA-256 values for declared artifacts and reports missing or mismatched artifacts.

### Schema contract discovery

```python
from evidence_ai_core import list_schema_contracts, load_schema_contract

index = list_schema_contracts()
contract = load_schema_contract("query_job.json")
```

Schema discovery reads static schema files. It does not add runtime validation authority.

### Packet ZIP export

```python
from evidence_ai_core import export_packet_zip

result = export_packet_zip(packet_dir, "packet.zip")
print(result["export_status"])
```

Export creates a local ZIP archive from an existing packet directory. It uses deterministic archive entry ordering and preserves file bytes.

Export does not validate scientific content, run replay, execute notebooks, call adapters, touch source control, or promote state.

### Packet ZIP import preview

```python
from evidence_ai_core import preview_packet_zip

preview = preview_packet_zip("packet.zip")
print(preview["preview_status"])
```

Preview inspects the ZIP without extracting it. It rejects unsafe archive entries and reports required artifact, JSON, packet ID, record type, and declared hash preview status.

### Safe packet ZIP extraction

```python
from evidence_ai_core import extract_packet_zip

result = extract_packet_zip("packet.zip", "imported_packets")
print(result["import_status"])
```

Extraction first runs preview, then extracts under the caller-provided output root. It refuses unsafe entries and existing destinations unless overwrite is explicitly allowed.

Extraction does not execute anything.

### Static ZIP roundtrip contract

The test suite proves the static/local roundtrip path:

```text
create packet
export ZIP
preview ZIP
extract ZIP
verify extracted packet
load extracted packet
summarize extracted packet
compare original/exported/extracted packet IDs and artifacts
```

The roundtrip tests are contract tests. They do not add scientific validation or promotion authority.

### Bundle inventory

```python
from evidence_ai_core import inventory_packet_bundle, export_packet_inventory_jsonl

inventory = inventory_packet_bundle(
    "packets",
    recursive=True,
    kind_filter="all",
    status_filter="all",
    sort_by="relative-path",
    reverse=False,
)
print(inventory["record_type"])
```

Bundle inventory discovers local packet directories and packet ZIP files under a chosen root. It reports compact status for found candidates and records failed candidates without mutating or executing anything.

Inventory is discovery, not validation.

Inventory filters:

```text
kind_filter: all | dirs | zips
status_filter: all | passed | failed
```

Inventory sort keys:

```text
relative-path
name
kind
verification-status
```

The result reports both filtered candidate counts and the unfiltered candidate count.

### Inventory JSONL export

```python
from evidence_ai_core import export_packet_inventory_jsonl

result = export_packet_inventory_jsonl(
    "packets",
    "inventory.jsonl",
    recursive=True,
    kind_filter="zips",
    status_filter="passed",
    sort_by="name",
)
print(result["jsonl_record_count"])
```

`export_packet_inventory_jsonl()` writes one compact, sorted JSON object per filtered inventory candidate. It uses the same local discovery, filtering, and sorting contract as `inventory_packet_bundle()`.

The JSONL export is local reporting only. It does not mutate packets, extract ZIPs, execute packet contents, call models, contact networks, touch source control, validate scientific claims, or promote state.

## Public errors

```python
from evidence_ai_core import (
    EvidenceCoreError,
    PacketAlreadyExistsError,
    PacketExportError,
    PacketImportError,
    PacketInputError,
    PacketReadError,
    PacketVerificationError,
)
```

Package-owned errors are used for expected static/local API and CLI failures.

## v0.1 public API stability notes

The v0.1 public API is intentionally conservative and static/local. Documented public calls and exported package-owned errors should not change casually during the v0.1 line.

Stable-ish v0.1 surfaces:

- documented public functions exported from `evidence_ai_core.__all__`,
- package-owned error classes exported from `evidence_ai_core`,
- documented CLI command names,
- compact JSON output keys used by the documented CLI/API examples,
- static JSON Schema files and schema discovery results,
- package-data inclusion for `schemas/*.schema.json`.

Still internal before v1.0:

- helper modules and private functions,
- test helpers,
- undocumented implementation details,
- exact formatting of human-readable error text beyond clear failure meaning.

Allowed pre-v1.0 changes:

- additive JSON fields,
- compatibility aliases when useful,
- safety or authority-boundary corrections,
- naming corrections that prevent proof/validation/promotion confusion,
- packaging fixes that preserve the static/local contract.

Avoided changes:

- casual renames of documented API calls,
- casual CLI command renames,
- JSON key changes that break simple scripting without a safety reason,
- new runtime adapter dependencies,
- any name or behavior implying scientific proof, workflow promotion, source-control settlement, notebook execution, model calls, or retrieval execution.

## CLI usage

The CLI examples below use local files only. For a ready-made demo input, see `examples/static_minimal/` and `docs/EXAMPLES.md`.

### Create a static packet

```powershell
evidence-ai-core create-static --request-text "demo request" --source .\source.md --output-root .\packets
```

The command prints the created packet directory path.

### Create from a local request file

```powershell
evidence-ai-core create-static --request-file .\request.txt --source .\source.md --output-root .\packets
```

The request file is read locally as static input. It is not interpreted as an orchestration file.

### Verify a packet

```powershell
evidence-ai-core verify .\packets\<packet_id>
```

Valid packet verification returns `0`. Mechanical failure returns nonzero.

### Inspect a packet

```powershell
evidence-ai-core inspect .\packets\<packet_id>
```

Inspection is read-only and must not claim correctness, validation, replay proof, source-control settlement, or promotion.

### Compact summary

```powershell
evidence-ai-core summary .\packets\<packet_id>
```

### Manifest and hash summary

```powershell
evidence-ai-core manifest .\packets\<packet_id>
evidence-ai-core hash-summary .\packets\<packet_id>
```

### Schema discovery

```powershell
evidence-ai-core schema-index
evidence-ai-core schema-contract query_job.json
```

### Export a packet ZIP

```powershell
evidence-ai-core export-zip .\packets\<packet_id> --output-zip .\exports\packet.zip
```

Use `--overwrite` to replace an existing ZIP.

### Preview packet ZIP import

```powershell
evidence-ai-core import-zip-preview .\exports\packet.zip
```

Preview is read-only and performs no extraction.

### Safely extract a packet ZIP

```powershell
evidence-ai-core import-zip-extract .\exports\packet.zip --output-root .\imported_packets
```

Use `--overwrite` to replace an existing extracted packet directory.

### Inventory local packet bundles

```powershell
evidence-ai-core bundle-inventory .\packets
evidence-ai-core bundle-inventory .\packets --recursive
evidence-ai-core bundle-inventory .\packets --no-zips
```

Inventory reports local packet directories and packet ZIPs. It does not extract ZIPs, run replay, execute notebooks, call models, or mutate files.

Filter and sort examples:

```powershell
evidence-ai-core bundle-inventory .\packets --kind dirs
evidence-ai-core bundle-inventory .\packets --kind zips
evidence-ai-core bundle-inventory .\packets --status passed
evidence-ai-core bundle-inventory .\packets --status failed
evidence-ai-core bundle-inventory .\packets --sort name
evidence-ai-core bundle-inventory .\packets --sort verification-status --reverse
```

### Export inventory JSONL

```powershell
evidence-ai-core bundle-inventory-jsonl .\packets --output-jsonl .\inventory.jsonl
evidence-ai-core bundle-inventory-jsonl .\packets --output-jsonl .\inventory.jsonl --kind zips --status passed --sort name
evidence-ai-core bundle-inventory-jsonl .\packets --output-jsonl .\inventory.jsonl --recursive --overwrite
```

`bundle-inventory-jsonl` writes one compact JSON object per filtered/sorted inventory candidate. The command returns a JSON export result that includes candidate counts, JSONL line count, bytes written, output path, filters, sort options, authority flags, and evidence-is-not-proof language.

Supported inventory options:

```text
--kind all|dirs|zips
--status all|passed|failed
--sort relative-path|name|kind|verification-status
--reverse
```

### Pretty JSON output

JSON-producing commands emit compact sorted JSON by default. Use `--pretty` for indented sorted JSON.

Examples:

```powershell
evidence-ai-core verify .\packets\<packet_id> --pretty
evidence-ai-core summary .\packets\<packet_id> --pretty
evidence-ai-core bundle-inventory .\packets --pretty
evidence-ai-core bundle-inventory-jsonl .\packets --output-jsonl .\inventory.jsonl --pretty
```

## CLI output rule

`create-static` prints a packet path.

Other JSON-producing commands return stable JSON.

Default JSON:

- compact,
- single-line,
- sorted keys.

Pretty JSON:

- indented,
- sorted keys.

## Development checkpoint

Current validated implementation lane:

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
slice_028_readme_code_status_inventory_jsonl_update
slice_029_v0_1_contract_cleanup_audit
slice_030_docs_examples_alignment
slice_031_packaging_release_polish
slice_032_public_api_stability_notes
slice_033_v0_1_release_candidate_closeout
```

Current local validation bundle:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_core.py tests/test_schema_contract.py tests/test_cli.py tests/test_cli_json_output.py tests/test_no_external_actions.py tests/test_api_contract.py tests/test_verification_result_contract.py tests/test_packet_reader.py tests/test_packet_summary.py tests/test_manifest.py tests/test_schema_index.py tests/test_packet_export.py tests/test_packet_import.py tests/test_packet_zip_roundtrip.py tests/test_packet_inventory.py tests/test_packaging.py
```

Expected current result:

```text
132 passed
```

## Design posture

This project deliberately separates evidence from proof.

`evidence-ai-core` can tell you whether a packet is structurally coherent, whether required artifacts exist, whether hashes match, whether record IDs are consistent, whether authority flags stayed conservative, whether a packet archive can be safely previewed or extracted, whether the static ZIP roundtrip mechanics preserve identity and artifacts, and what packet-like bundles exist under a local root.

It cannot tell you whether a scientific answer is true.

That boundary is the product.
