from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .constants import AUTHORITY_FLAGS, JSON_ARTIFACTS, REQUIRED_ARTIFACTS
from .verify import verify_packet


def inspect_packet(packet_dir: str | Path) -> dict[str, Any]:
    """Return a read-only summary of an evidence packet.

    Inspection is deliberately mechanical. It reports packet shape and authority
    boundaries; it does not validate scientific correctness, replay work, or
    promote state.
    """
    packet_dir = Path(packet_dir)
    verification = verify_packet(packet_dir)
    parsed_records = _read_json_records(packet_dir)
    packet_id = verification.get("packet_id") or _first_packet_id(parsed_records)

    return {
        "schema_version": "0.1",
        "record_type": "packet_inspection_summary",
        "packet_id": packet_id,
        "packet_dir": str(packet_dir),
        "verification_status": verification["verification_status"],
        "required_artifacts": [
            {"path": name, "exists": (packet_dir / name).exists()}
            for name in REQUIRED_ARTIFACTS
        ],
        "authority_flags": _collect_authority_flags(parsed_records),
        "checks": verification["checks"],
        "errors": verification["errors"],
        "warnings": verification["warnings"],
        "authority_note": (
            "Evidence is not proof. Inspection is read-only and does not prove "
            "correctness, validation, replay, promotion, or citation support."
        ),
    }


def _read_json_records(packet_dir: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for name in JSON_ARTIFACTS:
        path = packet_dir / name
        if not path.exists():
            continue
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(loaded, dict):
            records[name] = loaded
    return records


def _first_packet_id(records: dict[str, dict[str, Any]]) -> str | None:
    for record in records.values():
        packet_id = record.get("packet_id")
        if isinstance(packet_id, str) and packet_id:
            return packet_id
    return None


def _collect_authority_flags(records: dict[str, dict[str, Any]]) -> dict[str, bool]:
    collected = dict(AUTHORITY_FLAGS)
    for record in records.values():
        flags = record.get("authority_flags")
        if not isinstance(flags, dict):
            continue
        for key in AUTHORITY_FLAGS:
            if flags.get(key) is True:
                collected[key] = True
    return collected
