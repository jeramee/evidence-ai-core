from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import PurePosixPath
from typing import Any


TRACE_LAB_EXPORT_MANIFEST = "trace_lab_export_manifest.json"

REQUIRED_TRACE_LAB_BOUNDARY_NOTES = (
    "evidence != truth",
    "operational validation != scientific validity",
    "approval record != agent permission",
    "dry-run != physical execution",
    "NeuML handoff != claim promotion",
    "simulated adapter != hardware adapter",
)

REQUIRED_FALSE_AUTHORITY_FLAGS = (
    "agent_approved",
    "physical_execution_completed",
    "scientific_truth_validated",
    "state_promoted",
    "claims_promoted",
    "network_calls_performed",
    "package_installation_performed",
    "hardware_access_performed",
)


def preview_tracelab_bundle(bundle_zip: str) -> dict[str, Any]:
    """Preview a TraceLab export bundle without extraction or execution.

    This is an acceptance-boundary inspection only. It does not convert the
    TraceLab bundle into a native EvidenceAI packet, execute TraceLab code,
    unpack the ZIP, call networks, touch source control, validate scientific
    truth, or promote claims.
    """

    errors: list[str] = []
    warnings: list[str] = []
    manifest: dict[str, Any] = {}
    names: set[str] = set()

    try:
        with zipfile.ZipFile(bundle_zip) as bundle:
            names = _safe_zip_names(bundle)

            if TRACE_LAB_EXPORT_MANIFEST not in names:
                errors.append(f"missing required TraceLab manifest: {TRACE_LAB_EXPORT_MANIFEST}")
            else:
                try:
                    manifest = json.loads(bundle.read(TRACE_LAB_EXPORT_MANIFEST).decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    errors.append(f"TraceLab export manifest is not valid UTF-8 JSON: {exc}")

            if manifest:
                errors.extend(_validate_manifest_shape(manifest))
                errors.extend(_validate_declared_bundle_files(bundle, names, manifest))

    except FileNotFoundError:
        errors.append(f"TraceLab bundle does not exist: {bundle_zip}")
    except zipfile.BadZipFile as exc:
        errors.append(f"TraceLab bundle is not a valid ZIP file: {exc}")

    preview_status = "passed_tracelab_bundle_preview" if not errors else "failed_tracelab_bundle_preview"

    return {
        "schema_version": "0.1",
        "record_type": "tracelab_bundle_preview",
        "preview_status": preview_status,
        "bundle_path": str(bundle_zip),
        "bundle_format": "zip",
        "manifest_path": TRACE_LAB_EXPORT_MANIFEST,
        "trace_lab_record_type": manifest.get("record_type") if manifest else None,
        "trace_lab_export_scope": manifest.get("export_scope") if manifest else None,
        "trace_lab_source_validation_status": manifest.get("source_validation_status") if manifest else None,
        "bundle_file_count": manifest.get("bundle_file_count", 0) if manifest else 0,
        "zip_entry_count": len(names),
        "extraction_performed": False,
        "execution_performed": False,
        "network_calls_performed": False,
        "hardware_access_performed": False,
        "source_control_touched": False,
        "claims_promoted": False,
        "errors": errors,
        "warnings": warnings,
        "authority_note": (
            "TraceLab bundle preview is read-only package inspection. It does not "
            "validate scientific truth, execute the bundle, unpack files, or promote claims."
        ),
    }


def _safe_zip_names(bundle: zipfile.ZipFile) -> set[str]:
    names: set[str] = set()

    for name in bundle.namelist():
        if name.endswith("/"):
            continue

        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts:
            raise zipfile.BadZipFile(f"unsafe zip entry: {name}")

        names.add(path.as_posix())

    return names


def _validate_manifest_shape(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if manifest.get("record_type") != "trace_lab_export_manifest":
        errors.append("TraceLab export manifest record_type must be trace_lab_export_manifest.")

    if manifest.get("export_scope") != "operational_simulation_only":
        errors.append("TraceLab export manifest export_scope must be operational_simulation_only.")

    if manifest.get("export_status") != "ready_for_local_zip_export":
        errors.append("TraceLab export manifest export_status must be ready_for_local_zip_export.")

    if manifest.get("source_validation_status") != "passed_operational_checks":
        errors.append(
            "TraceLab export manifest source_validation_status must be passed_operational_checks."
        )

    boundary_notes = manifest.get("boundary_notes", [])
    for note in REQUIRED_TRACE_LAB_BOUNDARY_NOTES:
        if note not in boundary_notes:
            errors.append(f"TraceLab export manifest is missing boundary note: {note}")

    authority_flags = manifest.get("authority_flags", {})
    for flag_name in REQUIRED_FALSE_AUTHORITY_FLAGS:
        if authority_flags.get(flag_name) is not False:
            errors.append(f"TraceLab export manifest authority flag must remain false: {flag_name}")

    bundle_files = manifest.get("bundle_files", [])
    if not isinstance(bundle_files, list):
        errors.append("TraceLab export manifest bundle_files must be a list.")
        return errors

    if manifest.get("bundle_file_count") != len(bundle_files):
        errors.append("TraceLab export manifest bundle_file_count does not match bundle_files length.")

    return errors


def _validate_declared_bundle_files(
    bundle: zipfile.ZipFile,
    names: set[str],
    manifest: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    bundle_files = manifest.get("bundle_files", [])

    if not isinstance(bundle_files, list):
        return errors

    declared_paths: set[str] = set()

    for index, item in enumerate(bundle_files):
        if not isinstance(item, dict):
            errors.append(f"TraceLab export manifest bundle_files[{index}] must be an object.")
            continue

        raw_path = item.get("path")
        if not isinstance(raw_path, str):
            errors.append(f"TraceLab export manifest bundle_files[{index}] is missing path.")
            continue

        path = PurePosixPath(raw_path)
        if path.is_absolute() or ".." in path.parts:
            errors.append(f"TraceLab export manifest bundle_files[{index}] has unsafe path.")
            continue

        safe_path = path.as_posix()
        declared_paths.add(safe_path)

        if safe_path not in names:
            errors.append(f"TraceLab bundle is missing declared file: {safe_path}")
            continue

        data = bundle.read(safe_path)

        expected_size = item.get("size_bytes")
        if isinstance(expected_size, int) and len(data) != expected_size:
            errors.append(f"TraceLab bundle file size mismatch: {safe_path}")

        expected_hash = item.get("hash")
        if isinstance(expected_hash, str):
            actual_hash = hashlib.sha256(data).hexdigest()
            if actual_hash != expected_hash:
                errors.append(f"TraceLab bundle file hash mismatch: {safe_path}")

    allowed_names = declared_paths | {TRACE_LAB_EXPORT_MANIFEST}
    unexpected_names = sorted(names - allowed_names)
    if unexpected_names:
        errors.append(f"TraceLab bundle contains unexpected files: {unexpected_names}")

    return errors
