from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .constants import (
    AUTHORITY_FLAGS,
    EXPECTED_RECORD_TYPES,
    JSON_ARTIFACTS,
    REQUIRED_ARTIFACTS,
)
from .hashes import sha256_file


REQUIRED_FIELDS_BY_ARTIFACT: dict[str, tuple[str, ...]] = {
    "query_job.json": (
        "schema_version",
        "record_type",
        "packet_id",
        "job_id",
        "created_at",
        "request_text",
        "input_refs",
        "authority_flags",
        "status",
    ),
    "retrieval_record.json": (
        "schema_version",
        "record_type",
        "packet_id",
        "retrieval_id",
        "retrieval_mode",
        "query_ref",
        "results",
        "retrieval_status",
    ),
    "source_citations.json": (
        "schema_version",
        "record_type",
        "packet_id",
        "citation_set_id",
        "citation_status",
        "citations",
    ),
    "notebook_run_record.json": (
        "schema_version",
        "record_type",
        "packet_id",
        "run_id",
        "execution_mode",
        "execution_status",
        "authority_flags",
    ),
    "environment_report.json": (
        "schema_version",
        "record_type",
        "packet_id",
        "environment_id",
        "captured_at",
        "platform",
        "python",
        "raw_environment_dumped",
        "redaction_status",
    ),
    "artifact_manifest.json": (
        "schema_version",
        "record_type",
        "packet_id",
        "artifact_manifest_id",
        "artifact_status",
        "artifacts",
        "authority_flags",
    ),
    "replay_manifest.json": (
        "schema_version",
        "record_type",
        "packet_id",
        "replay_id",
        "replay_status",
        "required_files",
        "verification_checks",
        "limitations",
    ),
}


def verify_packet(packet_dir: str | Path) -> dict[str, Any]:
    packet_dir = Path(packet_dir)

    checks: list[dict[str, Any]] = []
    errors: list[str] = []
    warnings: list[str] = []

    def add(check_id: str, status: str, details: list[str] | None = None) -> None:
        details = details or []
        checks.append({"check_id": check_id, "status": status, "details": details})
        if status == "failed":
            errors.extend(details)

    missing = [name for name in REQUIRED_ARTIFACTS if not (packet_dir / name).exists()]
    add("required_files_exist", "failed" if missing else "passed", missing)

    parsed: dict[str, dict[str, Any]] = {}
    json_errors: list[str] = []

    for name in JSON_ARTIFACTS:
        path = packet_dir / name
        if not path.exists():
            continue

        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            json_errors.append(f"{name}: invalid JSON: {exc}")
            continue

        if not isinstance(loaded, dict):
            json_errors.append(f"{name}: top-level JSON value must be an object")
            continue

        parsed[name] = loaded

    add("json_files_parse", "failed" if json_errors else "passed", json_errors)

    field_errors: list[str] = []
    for name, record in parsed.items():
        required_fields = REQUIRED_FIELDS_BY_ARTIFACT.get(
            name,
            ("schema_version", "record_type", "packet_id"),
        )

        for field in required_fields:
            if field not in record:
                field_errors.append(f"{name}: missing {field}")

        expected_record_type = EXPECTED_RECORD_TYPES.get(name)
        if expected_record_type and record.get("record_type") != expected_record_type:
            field_errors.append(
                f"{name}: expected record_type {expected_record_type!r}, "
                f"got {record.get('record_type')!r}"
            )

    add("required_fields_present", "failed" if field_errors else "passed", field_errors)

    packet_ids = sorted(
        {
            record.get("packet_id")
            for record in parsed.values()
            if isinstance(record.get("packet_id"), str) and record.get("packet_id")
        }
    )
    add(
        "packet_id_consistent",
        "failed" if len(packet_ids) > 1 else "passed",
        packet_ids,
    )

    escalation_errors: list[str] = []
    for name, record in parsed.items():
        flags = record.get("authority_flags")
        if flags is None:
            continue

        if not isinstance(flags, dict):
            escalation_errors.append(f"{name}: authority_flags must be an object")
            continue

        for key, expected_value in AUTHORITY_FLAGS.items():
            actual_value = flags.get(key)
            if actual_value is not expected_value:
                escalation_errors.append(f"{name}: {key}={actual_value!r}")

        for key, actual_value in flags.items():
            if key not in AUTHORITY_FLAGS and actual_value is True:
                escalation_errors.append(f"{name}: unexpected authority flag {key}=True")

    add(
        "authority_flags_not_escalated",
        "failed" if escalation_errors else "passed",
        escalation_errors,
    )

    hash_errors: list[str] = []
    manifest = parsed.get("artifact_manifest.json", {})
    artifacts = manifest.get("artifacts", [])

    if manifest and not isinstance(artifacts, list):
        hash_errors.append("artifact_manifest.json: artifacts must be a list")
    elif isinstance(artifacts, list):
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                hash_errors.append("artifact_manifest.json: artifact entry must be an object")
                continue

            rel_path = artifact.get("path")
            if not rel_path:
                hash_errors.append("artifact_manifest.json: artifact missing path")
                continue

            hash_info = artifact.get("hash") or {}
            expected_hash = hash_info.get("value")

            if rel_path == "artifact_manifest.json" and expected_hash is None:
                continue

            artifact_path = packet_dir / rel_path

            if expected_hash is None:
                hash_errors.append(f"{rel_path}: missing sha256 hash")
                continue

            if not artifact_path.exists():
                hash_errors.append(f"{rel_path}: cannot verify hash because file is missing")
                continue

            actual_hash = sha256_file(artifact_path)
            if actual_hash != expected_hash:
                hash_errors.append(f"{rel_path}: hash mismatch")

    add("artifact_hashes_match", "failed" if hash_errors else "passed", hash_errors)

    if parsed.get("source_citations.json"):
        warnings.append("Citation support was not evaluated.")

    if parsed.get("replay_manifest.json", {}).get("replay_status") == "inspection_only":
        warnings.append("Replay is inspection-only.")

    status = "passed_mechanical_checks" if not errors else "failed_mechanical_checks"

    return {
        "schema_version": "0.1",
        "record_type": "verification_result",
        "packet_id": packet_ids[0] if len(packet_ids) == 1 else None,
        "verification_status": status,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "authority_note": "Mechanical verification is not scientific validation.",
    }
