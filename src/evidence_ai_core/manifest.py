from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .constants import (
    AUTHORITY_FLAGS,
    VERIFICATION_AUTHORITY_NOTE,
    VERIFICATION_LIMITATIONS,
    VERIFICATION_STATUS_FAILED,
    VERIFICATION_STATUS_PASSED,
)
from .errors import PacketInputError, PacketReadError
from .hashes import sha256_file


ARTIFACT_MANIFEST_READ_RESULT_RECORD_TYPE = "artifact_manifest_read_result"
ARTIFACT_HASH_SUMMARY_RECORD_TYPE = "artifact_hash_summary"
HASH_SUMMARY_SCOPE = "artifact_manifest_hash_summary_only"


def read_artifact_manifest(packet_dir: str | Path) -> dict[str, Any]:
    """Read only the packet artifact manifest and return a stable wrapper.

    This API parses local static packet metadata only. It does not update the
    manifest, repair hashes, execute files, validate scientific claims, or
    promote state.
    """
    packet_path = _validate_packet_dir(packet_dir)
    manifest_path = packet_path / "artifact_manifest.json"

    if not manifest_path.exists():
        raise PacketReadError(f"artifact_manifest.json does not exist: {manifest_path}")

    manifest = _load_manifest_json(manifest_path)
    artifacts = manifest.get("artifacts", [])
    if not isinstance(artifacts, list):
        raise PacketReadError("artifact_manifest.json: artifacts must be a list")

    return {
        "schema_version": "0.1",
        "record_type": ARTIFACT_MANIFEST_READ_RESULT_RECORD_TYPE,
        "packet_id": manifest.get("packet_id"),
        "packet_dir": str(packet_path),
        "manifest_path": "artifact_manifest.json",
        "artifact_count": len(artifacts),
        "artifact_manifest": manifest,
        "authority_flags": dict(AUTHORITY_FLAGS),
        "authority_note": (
            f"{VERIFICATION_AUTHORITY_NOTE} Reading the artifact manifest is read-only and "
            "does not prove correctness, validate claims, replay execution, repair hashes, or promote state."
        ),
        "limitations": list(VERIFICATION_LIMITATIONS),
    }


def summarize_artifact_hashes(packet_dir: str | Path) -> dict[str, Any]:
    """Return a compact hash summary for artifacts declared by the manifest."""
    manifest_result = read_artifact_manifest(packet_dir)
    packet_path = Path(manifest_result["packet_dir"])
    manifest = manifest_result["artifact_manifest"]
    artifacts = [_summarize_manifest_artifact(packet_path, artifact) for artifact in manifest["artifacts"]]

    missing_count = sum(1 for artifact in artifacts if artifact["hash_status"] == "missing_artifact")
    mismatch_count = sum(1 for artifact in artifacts if artifact["hash_status"] == "hash_mismatch")
    hashed_count = sum(1 for artifact in artifacts if artifact["hash_status"] in {"hash_match", "hash_mismatch"})
    unhashed_count = sum(1 for artifact in artifacts if artifact["hash_status"] == "hash_not_recorded")
    malformed_count = sum(1 for artifact in artifacts if artifact["hash_status"] == "malformed_manifest_entry")
    status = (
        VERIFICATION_STATUS_FAILED
        if missing_count or mismatch_count or malformed_count
        else VERIFICATION_STATUS_PASSED
    )

    return {
        "schema_version": "0.1",
        "record_type": ARTIFACT_HASH_SUMMARY_RECORD_TYPE,
        "packet_id": manifest_result["packet_id"],
        "packet_dir": manifest_result["packet_dir"],
        "manifest_path": "artifact_manifest.json",
        "verification_status": status,
        "verification_scope": HASH_SUMMARY_SCOPE,
        "hash_algorithm": "sha256",
        "artifact_count": len(artifacts),
        "hashed_artifact_count": hashed_count,
        "unhashed_artifact_count": unhashed_count,
        "missing_artifact_count": missing_count,
        "hash_mismatch_count": mismatch_count,
        "malformed_entry_count": malformed_count,
        "artifacts": artifacts,
        "authority_flags": dict(AUTHORITY_FLAGS),
        "authority_note": (
            f"{VERIFICATION_AUTHORITY_NOTE} Hash summaries are read-only and do not prove correctness, "
            "validate claims, replay execution, repair hashes, or promote state."
        ),
        "limitations": list(VERIFICATION_LIMITATIONS),
    }


def _validate_packet_dir(packet_dir: str | Path) -> Path:
    packet_path = Path(packet_dir)
    if not packet_path.exists():
        raise PacketInputError(f"packet directory does not exist: {packet_path}")
    if not packet_path.is_dir():
        raise PacketInputError(f"packet path is not a directory: {packet_path}")
    return packet_path


def _load_manifest_json(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PacketReadError(f"artifact_manifest.json: invalid JSON: {exc}") from exc

    if not isinstance(loaded, dict):
        raise PacketReadError("artifact_manifest.json: top-level JSON value must be an object")
    if loaded.get("record_type") != "artifact_manifest":
        raise PacketReadError(
            f"artifact_manifest.json: expected record_type 'artifact_manifest', got {loaded.get('record_type')!r}"
        )
    return loaded


def _summarize_manifest_artifact(packet_dir: Path, artifact: Any) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        return {
            "path": None,
            "required": None,
            "exists": False,
            "hash_algorithm": "sha256",
            "expected_hash": None,
            "actual_hash": None,
            "hash_status": "malformed_manifest_entry",
        }

    rel_path = artifact.get("path")
    hash_info = artifact.get("hash") if isinstance(artifact.get("hash"), dict) else {}
    expected_hash = hash_info.get("value")
    hash_algorithm = hash_info.get("algorithm") or "sha256"
    required = artifact.get("required")

    if not isinstance(rel_path, str) or not rel_path:
        return {
            "path": rel_path,
            "required": required,
            "exists": False,
            "hash_algorithm": hash_algorithm,
            "expected_hash": expected_hash,
            "actual_hash": None,
            "hash_status": "malformed_manifest_entry",
        }

    path = packet_dir / rel_path
    if not path.exists():
        return {
            "path": rel_path,
            "required": required,
            "exists": False,
            "hash_algorithm": hash_algorithm,
            "expected_hash": expected_hash,
            "actual_hash": None,
            "hash_status": "missing_artifact",
        }

    if expected_hash is None:
        return {
            "path": rel_path,
            "required": required,
            "exists": True,
            "hash_algorithm": hash_algorithm,
            "expected_hash": None,
            "actual_hash": None,
            "hash_status": "hash_not_recorded",
        }

    actual_hash = sha256_file(path)
    return {
        "path": rel_path,
        "required": required,
        "exists": True,
        "hash_algorithm": hash_algorithm,
        "expected_hash": expected_hash,
        "actual_hash": actual_hash,
        "hash_status": "hash_match" if actual_hash == expected_hash else "hash_mismatch",
    }
