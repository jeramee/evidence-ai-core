from __future__ import annotations

from pathlib import Path
import json

from .constants import REQUIRED_ARTIFACTS, JSON_ARTIFACTS, AUTHORITY_FLAGS, EXPECTED_RECORD_TYPES
from .hashes import sha256_file

def verify_packet(packet_dir: str | Path) -> dict:
    packet_dir = Path(packet_dir)
    checks = []
    errors = []
    warnings = []

    def add(check_id: str, status: str, details=None):
        details = details or []
        checks.append({"check_id": check_id, "status": status, "details": details})
        if status == "failed":
            errors.extend(details)

    missing = [name for name in REQUIRED_ARTIFACTS if not (packet_dir / name).exists()]
    add("required_files_exist", "failed" if missing else "passed", missing)

    parsed = {}
    json_errors = []
    for name in JSON_ARTIFACTS:
        path = packet_dir / name
        if not path.exists():
            continue
        try:
            parsed[name] = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            json_errors.append(f"{name}: {exc}")
    add("json_files_parse", "failed" if json_errors else "passed", json_errors)

    field_errors = []
    for name, record in parsed.items():
        for field in ("schema_version", "record_type", "packet_id"):
            if field not in record:
                field_errors.append(f"{name}: missing {field}")
        expected = EXPECTED_RECORD_TYPES.get(name)
        if expected and record.get("record_type") != expected:
            field_errors.append(f"{name}: expected record_type {expected!r}")
    add("required_fields_present", "failed" if field_errors else "passed", field_errors)

    packet_ids = {record.get("packet_id") for record in parsed.values() if record.get("packet_id")}
    add("packet_id_consistent", "failed" if len(packet_ids) > 1 else "passed", sorted(packet_ids))

    escalation = []
    for name, record in parsed.items():
        flags = record.get("authority_flags")
        if flags:
            for key, expected in AUTHORITY_FLAGS.items():
                if flags.get(key) is not expected:
                    escalation.append(f"{name}: {key}={flags.get(key)!r}")
    add("authority_flags_not_escalated", "failed" if escalation else "passed", escalation)

    hash_errors = []
    manifest = parsed.get("artifact_manifest.json", {})
    for artifact in manifest.get("artifacts", []):
        rel = artifact.get("path")
        expected = (artifact.get("hash") or {}).get("value")
        if rel and expected and (packet_dir / rel).exists():
            actual = sha256_file(packet_dir / rel)
            if actual != expected:
                hash_errors.append(f"{rel}: hash mismatch")
    add("artifact_hashes_match", "failed" if hash_errors else "passed", hash_errors)

    if parsed.get("source_citations.json"):
        warnings.append("Citation support was not evaluated.")
    if parsed.get("replay_manifest.json", {}).get("replay_status") == "inspection_only":
        warnings.append("Replay is inspection-only.")

    status = "passed_mechanical_checks" if not errors else "failed_mechanical_checks"
    return {
        "schema_version": "0.1",
        "record_type": "verification_result",
        "packet_id": next(iter(packet_ids), None),
        "verification_status": status,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
        "authority_note": "Mechanical verification is not scientific validation.",
    }
