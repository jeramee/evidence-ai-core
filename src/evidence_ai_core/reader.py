from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .constants import (
    AUTHORITY_FLAGS,
    JSON_ARTIFACTS,
    REQUIRED_ARTIFACTS,
    VERIFICATION_AUTHORITY_NOTE,
    VERIFICATION_LIMITATIONS,
)
from .errors import PacketInputError, PacketReadError
from .verify import verify_packet


PACKET_READ_RESULT_RECORD_TYPE = "packet_read_result"


def load_packet(packet_dir: str | Path) -> dict[str, Any]:
    """Load a static evidence packet into a read-only in-memory structure.

    The reader is mechanical and local-only. It parses packet files and embeds
    the verification result, but it does not execute notebooks, models,
    adapters, source-control operations, or external services.
    """
    packet_path = Path(packet_dir)

    if not packet_path.exists():
        raise PacketInputError(f"packet directory does not exist: {packet_path}")
    if not packet_path.is_dir():
        raise PacketInputError(f"packet path is not a directory: {packet_path}")

    json_records = _load_json_records(packet_path)
    text_artifacts = _load_text_artifacts(packet_path)
    verification_result = verify_packet(packet_path)
    packet_id = verification_result.get("packet_id") or _first_packet_id(json_records)

    return {
        "schema_version": "0.1",
        "record_type": PACKET_READ_RESULT_RECORD_TYPE,
        "packet_id": packet_id,
        "packet_dir": str(packet_path),
        "artifact_names": list(REQUIRED_ARTIFACTS),
        "json_records": json_records,
        "text_artifacts": text_artifacts,
        "verification_result": verification_result,
        "verification_status": verification_result["verification_status"],
        "authority_flags": dict(AUTHORITY_FLAGS),
        "authority_note": (
            f"{VERIFICATION_AUTHORITY_NOTE} Loading a packet is read-only and "
            "does not prove correctness, validate claims, replay execution, or promote state."
        ),
        "limitations": list(VERIFICATION_LIMITATIONS),
    }


def _load_json_records(packet_dir: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}

    for name in JSON_ARTIFACTS:
        path = packet_dir / name
        if not path.exists():
            continue

        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise PacketReadError(f"{name}: invalid JSON: {exc}") from exc

        if not isinstance(loaded, dict):
            raise PacketReadError(f"{name}: top-level JSON value must be an object")

        records[name] = loaded

    return records


def _load_text_artifacts(packet_dir: Path) -> dict[str, str]:
    text_artifacts: dict[str, str] = {}

    for name in REQUIRED_ARTIFACTS:
        if name.endswith(".json"):
            continue

        path = packet_dir / name
        if path.exists():
            text_artifacts[name] = path.read_text(encoding="utf-8")

    return text_artifacts


def _first_packet_id(records: dict[str, dict[str, Any]]) -> str | None:
    for record in records.values():
        packet_id = record.get("packet_id")
        if isinstance(packet_id, str) and packet_id:
            return packet_id
    return None
