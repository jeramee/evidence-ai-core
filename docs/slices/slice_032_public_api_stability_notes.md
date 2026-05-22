# slice_032_public_api_stability_notes

## Current checkpoint

```text
slice_031_packaging_release_polish
132 passed
```

## Exact next target

Record v0.1 public API stability notes without changing production behavior.

## Why it is next

After packaging release polish, v0.1 release hardening needs explicit stability expectations for documented public functions, package-owned errors, CLI command names, JSON output shape, and schema contracts.

This keeps the project in freeze mode and prevents public API cleanup from becoming new feature work.

## Scope

Files updated:

```text
README.md
CODE_STATUS.md
TEST_STATUS.md
docs/API_STABILITY.md
docs/slices/slice_032_public_api_stability_notes.md
```

## Public API posture

The v0.1 public API is stable-ish, not permanently frozen before v1.0.

Documented public calls and package-owned errors should not change casually. Before v1.0, small breaking changes remain allowed when they protect the evidence model, prevent authority drift, correct unsafe naming, or fix packaging/contract errors.

## Acceptance criteria

- README includes v0.1 public API stability notes.
- `docs/API_STABILITY.md` exists.
- CODE_STATUS records `slice_032_public_api_stability_notes`.
- TEST_STATUS confirms no new test is required for this documentation-only slice.
- No production code behavior changes are made.
- No new user-facing Project 1 packet feature is introduced.

## Exact test status

No new test is required for this documentation-only slice because no production code, tests, schemas, CLI behavior, package metadata, or package data changed.

Current green bundle remains:

```text
132 passed
```

## Stop-line

Do not use public API stability notes to add adapters, notebook execution, model calls, network calls, source-control mutation, workflow orchestration, validation authority, promotion authority, RunLab behavior, or TraceLab behavior.
