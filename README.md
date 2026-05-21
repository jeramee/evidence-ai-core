# evidenceai-core

**Evidence packets for reproducible scientific RAG with `txtai`, `paperetl`, and `paperai`.**

`evidenceai-core` is a proposed provenance and evidence-packet layer for the NeuML ecosystem. It records what happened during an AI-assisted research run: what was requested, what was retrieved, what sources were cited, what context was assembled, what execution step occurred, what environment produced the output, what artifacts were generated, and what replay instructions exist.

Its core rule is simple:

> Evidence is not proof.

This project is designed to sit underneath higher-level tools. It is not a replacement for `txtai`, `paperetl`, `paperai`, notebooks, reports, peer review, or scientific judgment.

---

## Why this belongs in the NeuML stack

NeuML already has a strong AI research stack:

| Project | Existing role | Where `evidenceai-core` fits |
|---|---|---|
| [`txtai`](https://github.com/neuml/txtai) | Semantic search, embeddings, RAG, LLM orchestration, workflows, agents, and APIs | Supplies retrieval events, index references, query metadata, and context records |
| [`paperetl`](https://github.com/neuml/paperetl) | ETL for medical and scientific papers, including PDF/XML/CSV-style inputs | Supplies structured source metadata, source identifiers, source hashes, and citation locators |
| [`paperai`](https://github.com/neuml/paperai) | Semantic search and AI workflows for medical/scientific papers | Supplies generated reports, answer tables, and paper-level evidence artifacts |
| `evidenceai-core` | Evidence packet model, schemas, verifier, authority vocabulary, replay metadata | Packages the evidence trail without claiming that the result is scientifically proven |

The current gap is not answer generation. The gap is durable evidence preservation.

A RAG answer is not enough.  
A citation list is not enough.  
A notebook run is not enough.  
A rendered report is not enough.

A serious scientific RAG workflow should preserve the path from request to result.

---

## What this is

`evidenceai-core` is the small, reusable evidence/provenance core underneath higher-level research tools.

It provides:

- a minimum evidence packet format
- JSON record contracts
- artifact manifests
- replay manifests
- conservative authority flags
- packet verification
- future adapter boundaries for `txtai`, `paperetl`, `paperai`, notebooks, and reports

The goal is to make AI-assisted research outputs more inspectable, replay-aware, and honest about their limits.

---

## What this is not

This is not:

- a notebook platform
- a RAG framework
- a model server
- a workflow orchestrator
- a citation manager
- a dashboard
- an agent framework
- a scientific validator
- a truth engine
- a Git/source-control settlement tool

`evidenceai-core` does not claim that a generated answer is true merely because it was retrieved, cited, executed, or rendered.

---

## Minimum evidence packet

A minimum packet contains:

```text
evidence_packets/<packet_id>/
  query_job.json
  retrieval_record.json
  source_citations.json
  context_pack.md
  notebook_run_record.json
  environment_report.json
  artifact_manifest.json
  replay_manifest.json
```

### `query_job.json`

Records the request that started the run.

### `retrieval_record.json`

Records what was retrieved, from which index or corpus, with which configuration.

### `source_citations.json`

Records source identifiers, citation locators, source hashes where available, and support status.

### `context_pack.md`

A human-readable bundle of selected context used by a downstream notebook, report, or reviewer.

### `notebook_run_record.json`

Records execution status. In the first slice, this explicitly says `not_executed`.

### `environment_report.json`

Records declared-scope environment details without dumping private secrets.

### `artifact_manifest.json`

Lists packet files and generated artifacts with hashes where available.

### `replay_manifest.json`

Explains what can be inspected or replayed, and what cannot.

---

## Default authority flags

Every evidence packet should preserve conservative defaults:

```json
{
  "correctness_proven": false,
  "repo_mutated": false,
  "state_promoted": false,
  "source_control_touched": false
}
```

These flags are not decorative. They prevent evidence from being silently upgraded into validation or promotion.

---

## First build target

The first implementation slice should be:

```text
slice_001_static_minimal_evidence_packet
```

It creates and verifies a static/local evidence packet.

No `txtai`.  
No `paperetl`.  
No `paperai`.  
No model calls.  
No notebook execution.  
No source-control mutation.  
No network access.  
No validation or promotion claims.

The first job is to prove the record model, not the whole ecosystem.

---

## Future adapter flow

```text
paperetl
  -> source records / citation locators
  -> evidenceai-core packet records

txtai
  -> retrieval record / context pack inputs
  -> evidenceai-core packet records

paperai
  -> report artifacts / answer tables
  -> evidenceai-core artifact manifest

notebook runner
  -> executed notebook / run logs
  -> evidenceai-core notebook_run_record.json

replay/export layer
  -> replay attempt records / RO-Crate export
  -> evidenceai-core packet archive
```

Adapters execute external work. `evidenceai-core` records and verifies evidence.

---

## Verification model

The verifier may check:

- required files exist
- JSON files parse
- required fields exist
- `packet_id` is consistent across records
- artifact hashes match
- replay manifest includes required files
- authority flags remain conservative

The verifier must not check:

- scientific correctness
- source truth
- claim support
- methodology validity
- statistical soundness
- publication readiness
- peer-review status
- institutional acceptance

Mechanical verification is not scientific validation.

---

## Standards posture

`evidenceai-core` should align with standards without making the first slice heavy.

| Standard / ecosystem | Proposed role |
|---|---|
| W3C PROV | Future conceptual mapping for entities, activities, and agents |
| JSON Schema Draft 2020-12 | Future validation layer for packet records |
| RO-Crate | Future export format for research-object packaging |
| FAIR4RS | Research-software design principle |
| CITATION.cff / CodeMeta | Repository-level software citation metadata |
| SPDX / SBOM | Optional future dependency and license metadata |
| Software Heritage IDs | Optional future source-code artifact identifiers |
| OpenLineage | Optional future mapping for jobs, runs, and datasets |

The first version should use local files, JSON records, SHA-256 hashes, and simple mechanical checks.

---

## Suggested repository layout

```text
evidenceai-core/
  README.md
  pyproject.toml
  LICENSE
  CHANGELOG.md

  src/
    evidenceai_core/
      __init__.py
      constants.py
      ids.py
      paths.py
      hashes.py
      packet.py
      records.py
      schemas.py
      verify.py
      environment.py
      errors.py
      cli.py

  schemas/
    query_job.schema.json
    retrieval_record.schema.json
    source_citations.schema.json
    notebook_run_record.schema.json
    environment_report.schema.json
    artifact_manifest.schema.json
    replay_manifest.schema.json

  examples/
    static_minimal/
      inputs/
        request.txt
        source_a.md
      expected_packet/
        query_job.json
        retrieval_record.json
        source_citations.json
        context_pack.md
        notebook_run_record.json
        environment_report.json
        artifact_manifest.json
        replay_manifest.json

  docs/
    evidence_packet_model.md
    authority_vocabulary.md
    adapter_contracts.md
    standards_mapping.md

  tests/
    test_packet_creation.py
    test_packet_verification.py
    test_authority_flags.py
    test_artifact_manifest.py
    test_no_external_actions.py
```

---

## Python API sketch

```python
from evidenceai_core import create_static_packet, verify_packet

packet_dir = create_static_packet(
    request_text="Create a minimal evidence packet.",
    source_paths=["examples/static_minimal/inputs/source_a.md"],
    output_root="evidence_packets"
)

result = verify_packet(packet_dir)
```

---

## CLI sketch

```bash
evidenceai-core create-static \
  --request-file examples/static_minimal/inputs/request.txt \
  --source examples/static_minimal/inputs/source_a.md \
  --output-root evidence_packets

evidenceai-core verify evidence_packets/<packet_id>

evidenceai-core inspect evidence_packets/<packet_id>
```

---

## Roadmap

### Phase 0 - static evidence core

- Create static packets
- Write required artifacts
- Hash artifacts
- Verify required files and fields
- Preserve conservative authority flags

### Phase 1 - schema hardening

- Add JSON Schema Draft 2020-12 files
- Add schema validation tests
- Add structured verification results

### Phase 2 - txtai adapter contract

- Record query, index reference, retrieval configuration, retrieved chunks, scores, ranks, and source IDs
- Preserve retrieval context without claiming citation support

### Phase 3 - paperetl adapter contract

- Record parsed source metadata
- Preserve source identifiers and hashes
- Link source records to citation records

### Phase 4 - paperai adapter contract

- Record generated reports and answer tables
- Link report sections back to citations and retrieval records
- Preserve authority flags

### Phase 5 - notebook/report adapters

- Record Papermill or notebook execution
- Record rendered reports
- Preserve logs and environment metadata

### Phase 6 - archive/export layer

- Map packets to RO-Crate-style export metadata
- Add optional PROV mapping
- Add optional software citation metadata

---

## Development principles

- Evidence is not proof.
- Retrieval context is not validation.
- Notebook execution is not scientific correctness.
- Rendered reports are not durable truth.
- Missing context should be explicit.
- Every official run should be inspectable.
- Every generated report should point back to machine-readable records.
- No whole-home indexing.
- No hidden model downloads.
- No source-control mutation by default.
- Humans and institutions promote durable truth.

---

## References

- NeuML: https://neuml.com/
- txtai: https://github.com/neuml/txtai
- txtai documentation: https://neuml.github.io/txtai/
- txtai tutorial series: https://neuml.hashnode.dev/series/txtai-tutorial
- paperetl: https://github.com/neuml/paperetl
- paperai: https://github.com/neuml/paperai
- W3C PROV-DM: https://www.w3.org/TR/prov-dm/
- JSON Schema Draft 2020-12: https://json-schema.org/draft/2020-12
- RO-Crate: https://www.researchobject.org/ro-crate/specification/1.2/
- FAIR4RS: https://www.nature.com/articles/s41597-022-01710-x

---

## License

Apache-2.0 is recommended for alignment with `txtai`, `paperetl`, and `paperai`.
