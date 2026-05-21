from __future__ import annotations

from pathlib import Path
from typing import Any

from .constants import AUTHORITY_FLAGS, REQUIRED_ARTIFACTS, VERIFICATION_AUTHORITY_NOTE, VERIFICATION_LIMITATIONS
from .reader import load_packet


PACKET_SUMMARY_RECORD_TYPE = "packet_summary"


def summarize_packet(packet_dir: str | Path) -> dict[str, Any]:
    """Return a compact read-only packet summary.

    The summary is intentionally mechanical and static/local. It does not
    include full record contents and does not prove correctness, validate
    scientific claims, replay execution, or promote state.
    """
    loaded = load_packet(packet_dir)
    verification = loaded["verification_result"]
    artifacts = _summarize_artifacts(loaded)
    check_status_counts = _count_check_statuses(verification.get("checks", []))

    return {
        "schema_version": "0.1",
        "record_type": PACKET_SUMMARY_RECORD_TYPE,
        "packet_id": loaded["packet_id"],
        "packet_dir": loaded["packet_dir"],
        "artifact_count": len(artifacts),
        "required_artifact_count": len(REQUIRED_ARTIFACTS),
        "missing_artifact_count": sum(1 for artifact in artifacts if not artifact["exists"]),
        "artifacts": artifacts,
        "json_record_count": len(loaded["json_records"]),
        "text_artifact_count": len(loaded["text_artifacts"]),
        "verification_status": loaded["verification_status"],
        "verification_scope": verification["verification_scope"],
        "check_count": verification["check_count"],
        "error_count": verification["error_count"],
        "warning_count": verification["warning_count"],
        "check_status_counts": check_status_counts,
        "authority_flags": dict(AUTHORITY_FLAGS),
        "authority_note": (
            f"Evidence is not proof. {VERIFICATION_AUTHORITY_NOTE} Packet summaries are "
            "read-only and do not prove correctness, validate claims, replay execution, or promote state."
        ),
        "limitations": list(VERIFICATION_LIMITATIONS),
    }


def _summarize_artifacts(loaded: dict[str, Any]) -> list[dict[str, Any]]:
    json_records = loaded["json_records"]
    text_artifacts = loaded["text_artifacts"]
    artifacts: list[dict[str, Any]] = []

    for name in REQUIRED_ARTIFACTS:
        exists = name in json_records or name in text_artifacts
        artifact_type = "json" if name.endswith(".json") else "text"
        artifacts.append(
            {
                "path": name,
                "artifact_type": artifact_type,
                "required": True,
                "exists": exists,
            }
        )

    return artifacts


def _count_check_statuses(checks: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for check in checks:
        status = check.get("status")
        if not isinstance(status, str):
            status = "unknown"
        counts[status] = counts.get(status, 0) + 1
    return counts
