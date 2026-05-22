# Public API stability notes

Project: `evidence-ai-core`

Version lane: v0.1 release hardening

Core rule:

> Evidence is not proof.

## Purpose

This document records the v0.1 public API stability posture for Project 1 only.

`evidence-ai-core` is a low-level static/local evidence packet core. Its public API and CLI are intended to support packet mechanics, local inspection, local summaries, static schema discovery, ZIP import/export mechanics, bundle inventory, and inventory JSONL export.

It does not own workflow execution, retrieval execution, notebook execution, model calls, source-control mutation, scientific validation, or promotion authority.

## Public API stability level

For v0.1, the public API is **stable-ish**, not permanently frozen.

Documented calls and package-owned errors should not change casually. Before v1.0, small breaking changes may still be allowed when they protect the evidence model, prevent authority drift, correct unsafe naming, or fix packaging/contract errors.

## Documented public functions

The documented public function surface is:

```python
from evidence_ai_core import (
    create_static_packet,
    export_packet_inventory_jsonl,
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

These functions are static/local packet utilities. They must not call models, contact networks, run notebooks, execute retrieval engines, mutate source control, validate scientific truth, or promote state.

## Documented public errors

The documented public error surface is:

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

## CLI stability posture

The documented CLI commands are stable-ish for v0.1:

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

Command names should not be renamed casually. If a command name ever implies proof, validation authority, execution, or promotion, it should be corrected before v1.0 with compatibility notes where practical.

## JSON output stability posture

JSON-producing CLI/API outputs should prefer additive changes.

Stable-ish behavior:

- compact sorted JSON by default for JSON-producing CLI commands,
- optional pretty sorted JSON when supported,
- verification status keys and authority fields preserved,
- inventory and JSONL fields preserved for simple scripting,
- evidence-not-proof language preserved where authority could be misunderstood.

Allowed before v1.0:

- additive fields,
- clearer authority notes,
- additional warnings or limitations,
- fixes to unsafe or misleading key names.

Avoid unless safety requires it:

- removing documented keys,
- renaming documented keys,
- changing success/failure status values,
- changing CLI exit behavior for documented success/failure cases.

## Schema stability posture

Static JSON Schema files are contract-bearing for v0.1.

Schema changes should be explicit and conservative. Additive schema metadata is safer than removing required fields or changing record-type meaning.

Packaged schema data under `src/evidence_ai_core/schemas/` must stay aligned with root `schemas/` during v0.1 release hardening.

## Internal surfaces

The following are internal before v1.0:

- implementation modules beyond documented exports,
- helper functions not exported from `evidence_ai_core`,
- test helpers,
- exact internal sorting/helper logic,
- exact wording of non-contractual human-readable errors.

## Stop-line

Do not use public API stability work to add new user-facing Project 1 packet features.

Do not add adapters, notebook execution, model calls, network calls, source-control mutation, workflow orchestration, validation authority, promotion authority, RunLab behavior, or TraceLab behavior.
