# slice_030_docs_examples_alignment

## Current checkpoint

```text
slice_029_v0_1_contract_cleanup_audit
129 passed
```

## Exact next target

Align README, repository examples, and example documentation with the current v0.1 static/local packet surface.

## Why it is next

After the v0.1 stop-line and contract cleanup audit, the remaining release-hardening lane should make the existing static minimal example usable and documented without adding new production behavior.

## Scope

Updated files:

```text
README.md
CODE_STATUS.md
docs/EXAMPLES.md
examples/static_minimal/README.md
docs/slices/slice_030_docs_examples_alignment.md
```

This slice documents how to use existing CLI/API behavior with the existing static example inputs.

## Non-goals

This slice does not add production code, tests, schemas, runtime dependencies, notebook execution, model calls, retrieval execution, source-control mutation, validation authority, promotion authority, RunLab behavior, or TraceLab behavior.

## Example behavior documented

The example documentation covers:

- local packet creation from `examples/static_minimal/inputs/request.txt`;
- local source input from `examples/static_minimal/inputs/source_a.md`;
- mechanical verification;
- read-only inspection and summary;
- manifest and hash summary;
- schema discovery;
- ZIP export, preview, extraction, bundle inventory, and inventory JSONL export.

## Test posture

No new test is required for this documentation/examples-only slice because no production code, tests, schemas, or CLI behavior changed.

Current code checkpoint remains:

```text
129 passed
```

## Acceptance criteria

- README points to `examples/static_minimal/` and `docs/EXAMPLES.md`.
- `docs/EXAMPLES.md` documents the static/local example workflow.
- `examples/static_minimal/README.md` gives a compact local walkthrough.
- CODE_STATUS records the examples/docs alignment slice.
- No new user-facing Project 1 feature is introduced.
- Boundary language remains clear: evidence is not proof.

## Stop-line

Stop after docs/examples alignment. Do not add runtime integrations, adapters, notebook execution, retrieval execution, validation authority, promotion authority, or new Project 1 feature scope.
