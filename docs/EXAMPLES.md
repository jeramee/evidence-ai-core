# evidence-ai-core examples

This document describes the static/local examples included with Project 1, `evidence-ai-core`.

Core rule:

> Evidence is not proof.

The examples are designed to exercise packet mechanics only. They do not execute notebooks, call models, run retrieval systems, contact networks, mutate source control, validate scientific truth, or promote state.

## Static minimal example

Example location:

```text
examples/static_minimal/
```

Included input files:

```text
examples/static_minimal/inputs/request.txt
examples/static_minimal/inputs/source_a.md
```

The request file contains a short static request. The source file contains a small local Markdown source.

## Create a packet

From the repository root:

```powershell
evidence-ai-core create-static --request-file .\examples\static_minimal\inputs\request.txt --source .\examples\static_minimal\inputs\source_a.md --output-root .\examples\static_minimal\packets
```

The command prints the created packet directory path. The packet directory name is the packet ID.

## Inspect and verify locally

Replace `<packet_id>` with the printed packet directory name:

```powershell
evidence-ai-core verify .\examples\static_minimal\packets\<packet_id> --pretty
evidence-ai-core inspect .\examples\static_minimal\packets\<packet_id> --pretty
evidence-ai-core summary .\examples\static_minimal\packets\<packet_id> --pretty
```

These commands are local and read-only after packet creation. `verify` performs mechanical packet checks only.

## Manifest, hashes, and schema discovery

```powershell
evidence-ai-core manifest .\examples\static_minimal\packets\<packet_id> --pretty
evidence-ai-core hash-summary .\examples\static_minimal\packets\<packet_id> --pretty
evidence-ai-core schema-index --pretty
evidence-ai-core schema-contract query_job.json --pretty
```

These commands expose static packet metadata and schema contracts. They do not add scientific validation authority.

## Export, preview, extract, and inventory

```powershell
evidence-ai-core export-zip .\examples\static_minimal\packets\<packet_id> --output-zip .\examples\static_minimal\exports\packet.zip --overwrite
evidence-ai-core import-zip-preview .\examples\static_minimal\exports\packet.zip --pretty
evidence-ai-core import-zip-extract .\examples\static_minimal\exports\packet.zip --output-root .\examples\static_minimal\imported --overwrite
evidence-ai-core bundle-inventory .\examples\static_minimal --recursive --pretty
evidence-ai-core bundle-inventory-jsonl .\examples\static_minimal --recursive --output-jsonl .\examples\static_minimal\inventory.jsonl --overwrite --pretty
```

Export/import/inventory commands remain local packet utilities. ZIP preview is read-only. ZIP extraction writes only under the explicit output root. Inventory JSONL writes a local report only.

## Boundary

The static minimal example proves that the package can create and inspect a mechanically coherent local evidence packet. It does not prove that a claim is true, that a retrieval result is correct, that a notebook ran, that a report is valid, or that any state should be promoted.
