from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any
from zipfile import BadZipFile, ZipFile

from .constants import (
    AUTHORITY_FLAGS,
    EXPECTED_RECORD_TYPES,
    JSON_ARTIFACTS,
    REQUIRED_ARTIFACTS,
    VERIFICATION_AUTHORITY_NOTE,
    VERIFICATION_LIMITATIONS,
    VERIFICATION_STATUS_FAILED,
    VERIFICATION_STATUS_PASSED,
)
from .errors import PacketImportError, PacketInputError


PACKET_ZIP_IMPORT_PREVIEW_RECORD_TYPE = "packet_zip_import_preview_result"
PACKET_ZIP_IMPORT_PREVIEW_SCOPE = "static_zip_preview_only_no_extraction"


def preview_packet_zip(zip_path: str | Path) -> dict[str, Any]:
    """Preview a static packet ZIP without extracting it.

    This API performs local ZIP inspection only. It does not extract files,
    execute packet contents, call models, run notebooks, contact networks,
    mutate source control, validate scientific claims, or promote state.
    """
    archive_path = _validate_zip_path(zip_path)

    try:
        with ZipFile(archive_path) as archive:
            infos = [info for info in archive.infolist() if not info.is_dir()]
            entry_names = [info.filename for info in infos]
            unsafe_entries = [name for name in entry_names if not _is_safe_zip_entry(name)]
            if unsafe_entries:
                raise PacketImportError(f"unsafe ZIP entry detected: {unsafe_entries[0]}")

            archive_root = _single_archive_root(entry_names)
            relative_names = [_strip_archive_root(name, archive_root) for name in entry_names]
            relative_name_set = set(relative_names)

            json_records = _load_json_records_from_archive(archive, archive_root, relative_name_set)
            packet_ids = sorted(
                {
                    record.get("packet_id")
                    for record in json_records.values()
                    if isinstance(record.get("packet_id"), str) and record.get("packet_id")
                }
            )
            record_type_errors = _record_type_errors(json_records)
            missing_required = [name for name in REQUIRED_ARTIFACTS if name not in relative_name_set]
            declared_artifacts = _summarize_declared_artifacts(archive, archive_root, json_records)
    except BadZipFile as exc:
        raise PacketImportError(f"invalid ZIP archive: {archive_path}") from exc

    hash_mismatch_count = sum(1 for artifact in declared_artifacts if artifact["hash_status"] == "hash_mismatch")
    missing_declared_count = sum(1 for artifact in declared_artifacts if artifact["hash_status"] == "missing_artifact")
    malformed_manifest_count = sum(
        1 for artifact in declared_artifacts if artifact["hash_status"] == "malformed_manifest_entry"
    )
    failed = bool(
        missing_required
        or len(packet_ids) != 1
        or record_type_errors
        or hash_mismatch_count
        or missing_declared_count
        or malformed_manifest_count
    )

    return {
        "schema_version": "0.1",
        "record_type": PACKET_ZIP_IMPORT_PREVIEW_RECORD_TYPE,
        "packet_id": packet_ids[0] if len(packet_ids) == 1 else None,
        "zip_path": str(archive_path),
        "preview_status": "preview_failed" if failed else "previewed",
        "import_status": "not_imported_preview_only",
        "verification_status": VERIFICATION_STATUS_FAILED if failed else VERIFICATION_STATUS_PASSED,
        "verification_scope": PACKET_ZIP_IMPORT_PREVIEW_SCOPE,
        "archive_format": "zip",
        "archive_root": archive_root,
        "zip_entry_count": len(entry_names),
        "file_count": len(entry_names),
        "required_artifact_count": len(REQUIRED_ARTIFACTS),
        "present_required_artifact_count": len(REQUIRED_ARTIFACTS) - len(missing_required),
        "missing_required_artifact_count": len(missing_required),
        "missing_required_artifacts": missing_required,
        "json_record_count": len(json_records),
        "packet_id_count": len(packet_ids),
        "packet_ids": packet_ids,
        "record_type_error_count": len(record_type_errors),
        "record_type_errors": record_type_errors,
        "declared_artifact_count": len(declared_artifacts),
        "hash_algorithm": "sha256",
        "hash_mismatch_count": hash_mismatch_count,
        "missing_declared_artifact_count": missing_declared_count,
        "malformed_manifest_entry_count": malformed_manifest_count,
        "artifacts": declared_artifacts,
        "extraction_performed": False,
        "unsafe_entry_count": 0,
        "authority_flags": dict(AUTHORITY_FLAGS),
        "authority_note": (
            f"{VERIFICATION_AUTHORITY_NOTE} ZIP import preview is read-only and does not extract files, "
            "prove correctness, validate claims, replay execution, touch source control, or promote state."
        ),
        "limitations": list(VERIFICATION_LIMITATIONS)
        + ["does_not_extract_zip_archives", "does_not_import_or_write_packet_files"],
    }


def _validate_zip_path(zip_path: str | Path) -> Path:
    path = Path(zip_path)
    if not path.exists():
        raise PacketInputError(f"ZIP file does not exist: {path}")
    if not path.is_file():
        raise PacketInputError(f"ZIP path is not a file: {path}")
    if path.suffix.lower() != ".zip":
        raise PacketInputError(f"ZIP path must end with .zip: {path}")
    return path


def _is_safe_zip_entry(name: str) -> bool:
    normalized = name.replace("\\", "/")
    if normalized.startswith("/") or normalized.startswith("~"):
        return False
    parts = PurePosixPath(normalized).parts
    if not parts:
        return False
    if any(part in {"", ".", ".."} for part in parts):
        return False
    if any(":" in part for part in parts):
        return False
    return True


def _single_archive_root(entry_names: list[str]) -> str:
    if not entry_names:
        raise PacketImportError("ZIP archive contains no files")
    roots = sorted({name.replace("\\", "/").split("/", 1)[0] for name in entry_names})
    if len(roots) != 1:
        raise PacketImportError("ZIP archive must contain exactly one packet root directory")
    return roots[0]


def _strip_archive_root(name: str, archive_root: str) -> str:
    normalized = name.replace("\\", "/")
    prefix = f"{archive_root}/"
    if not normalized.startswith(prefix):
        raise PacketImportError(f"ZIP entry is outside archive root {archive_root!r}: {name}")
    rel_path = normalized[len(prefix) :]
    if not rel_path:
        raise PacketImportError(f"ZIP entry has empty relative path: {name}")
    return rel_path


def _load_json_records_from_archive(
    archive: ZipFile,
    archive_root: str,
    relative_name_set: set[str],
) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for artifact_name in JSON_ARTIFACTS:
        if artifact_name not in relative_name_set:
            continue
        entry_name = f"{archive_root}/{artifact_name}"
        try:
            loaded = json.loads(archive.read(entry_name).decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise PacketImportError(f"{artifact_name}: invalid JSON in ZIP: {exc}") from exc
        if not isinstance(loaded, dict):
            raise PacketImportError(f"{artifact_name}: top-level JSON value must be an object")
        records[artifact_name] = loaded
    return records


def _record_type_errors(json_records: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for artifact_name, expected in EXPECTED_RECORD_TYPES.items():
        if artifact_name not in json_records:
            continue
        actual = json_records[artifact_name].get("record_type")
        if actual != expected:
            errors.append(f"{artifact_name}: expected record_type {expected!r}, got {actual!r}")
    return errors


def _summarize_declared_artifacts(
    archive: ZipFile,
    archive_root: str,
    json_records: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    manifest = json_records.get("artifact_manifest.json")
    if not manifest:
        return []

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list):
        return [
            {
                "path": None,
                "required": None,
                "exists": False,
                "hash_algorithm": "sha256",
                "expected_hash": None,
                "actual_hash": None,
                "hash_status": "malformed_manifest_entry",
            }
        ]

    archive_names = set(archive.namelist())
    return [_summarize_manifest_artifact(archive, archive_root, artifact, archive_names) for artifact in artifacts]


def _summarize_manifest_artifact(
    archive: ZipFile,
    archive_root: str,
    artifact: Any,
    archive_names: set[str],
) -> dict[str, Any]:
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
    required = artifact.get("required")
    hash_info = artifact.get("hash") if isinstance(artifact.get("hash"), dict) else {}
    expected_hash = hash_info.get("value")
    hash_algorithm = hash_info.get("algorithm") or "sha256"

    if not isinstance(rel_path, str) or not rel_path or not _is_safe_zip_entry(f"{archive_root}/{rel_path}"):
        return {
            "path": rel_path,
            "required": required,
            "exists": False,
            "hash_algorithm": hash_algorithm,
            "expected_hash": expected_hash,
            "actual_hash": None,
            "hash_status": "malformed_manifest_entry",
        }

    entry_name = f"{archive_root}/{rel_path}"
    if entry_name not in archive_names:
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

    actual_hash = hashlib.sha256(archive.read(entry_name)).hexdigest()
    return {
        "path": rel_path,
        "required": required,
        "exists": True,
        "hash_algorithm": hash_algorithm,
        "expected_hash": expected_hash,
        "actual_hash": actual_hash,
        "hash_status": "hash_match" if actual_hash == expected_hash else "hash_mismatch",
    }
