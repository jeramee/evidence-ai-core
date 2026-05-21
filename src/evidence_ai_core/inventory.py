from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .constants import AUTHORITY_FLAGS, REQUIRED_ARTIFACTS, VERIFICATION_AUTHORITY_NOTE, VERIFICATION_LIMITATIONS
from .errors import EvidenceCoreError, PacketExportError, PacketInputError
from .import_preview import preview_packet_zip
from .summary import summarize_packet


PACKET_BUNDLE_INVENTORY_RECORD_TYPE = "packet_bundle_inventory"
PACKET_BUNDLE_INVENTORY_SCOPE = "static_local_packet_bundle_inventory"
PACKET_BUNDLE_INVENTORY_JSONL_EXPORT_RECORD_TYPE = "packet_bundle_inventory_jsonl_export"
PACKET_BUNDLE_INVENTORY_JSONL_EXPORT_SCOPE = "static_local_packet_bundle_inventory_jsonl_export"
INVENTORY_KIND_FILTERS = {"all", "dirs", "zips"}
INVENTORY_STATUS_FILTERS = {"all", "passed", "failed"}
INVENTORY_SORT_FIELDS = {"relative-path", "name", "kind", "verification-status"}


def inventory_packet_bundle(
    root: str | Path,
    *,
    recursive: bool = False,
    include_zips: bool = True,
    kind_filter: str = "all",
    status_filter: str = "all",
    sort_by: str = "relative-path",
    reverse: bool = False,
) -> dict[str, Any]:
    """Inventory local packet directories and packet ZIPs under a root.

    This is static/local discovery only. It reads packet summaries and ZIP
    previews without executing packet contents, calling models, contacting
    networks, touching source control, validating scientific claims, or
    promoting state.
    """
    root_path = _validate_inventory_root(root)
    _validate_inventory_options(kind_filter, status_filter, sort_by)

    unfiltered_packet_dirs = [
        _inventory_packet_dir(path, root_path)
        for path in _packet_dir_candidates(root_path, recursive)
    ]
    unfiltered_packet_zips = (
        [_inventory_packet_zip(path, root_path) for path in _packet_zip_candidates(root_path, recursive)]
        if include_zips
        else []
    )

    filtered_candidates = _sort_candidates(
        _filter_candidates(
            [*unfiltered_packet_dirs, *unfiltered_packet_zips],
            kind_filter=kind_filter,
            status_filter=status_filter,
        ),
        sort_by=sort_by,
        reverse=reverse,
    )

    packet_dirs = [item for item in filtered_candidates if item["kind"] == "packet_dir"]
    packet_zips = [item for item in filtered_candidates if item["kind"] == "packet_zip"]
    failed_candidates = [
        item
        for item in filtered_candidates
        if item.get("verification_status") != "passed_mechanical_checks"
    ]

    return {
        "schema_version": "0.1",
        "record_type": PACKET_BUNDLE_INVENTORY_RECORD_TYPE,
        "root_path": str(root_path),
        "inventory_scope": PACKET_BUNDLE_INVENTORY_SCOPE,
        "inventory_status": "completed",
        "verification_status": (
            "passed_mechanical_checks" if not failed_candidates else "failed_mechanical_checks"
        ),
        "recursive": recursive,
        "include_zips": include_zips,
        "kind_filter": kind_filter,
        "status_filter": status_filter,
        "sort_by": sort_by,
        "sort_reverse": reverse,
        "unfiltered_candidate_count": len(unfiltered_packet_dirs) + len(unfiltered_packet_zips),
        "candidate_count": len(filtered_candidates),
        "packet_dir_count": len(packet_dirs),
        "packet_zip_count": len(packet_zips),
        "failed_candidate_count": len(failed_candidates),
        "candidates": filtered_candidates,
        "packet_dirs": packet_dirs,
        "packet_zips": packet_zips,
        "authority_flags": dict(AUTHORITY_FLAGS),
        "authority_note": (
            f"Evidence is not proof. {VERIFICATION_AUTHORITY_NOTE} Packet bundle inventory is local discovery only and does "
            "not prove correctness, validate claims, replay execution, touch source control, or promote state."
        ),
        "limitations": list(VERIFICATION_LIMITATIONS)
        + [
            "inventory_does_not_execute_packet_contents",
            "inventory_does_not_validate_scientific_claims",
            "inventory_is_not_import_or_export_authority",
        ],
    }


def export_packet_inventory_jsonl(
    root: str | Path,
    output_jsonl: str | Path,
    *,
    recursive: bool = False,
    include_zips: bool = True,
    kind_filter: str = "all",
    status_filter: str = "all",
    sort_by: str = "relative-path",
    reverse: bool = False,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Export a filtered static packet bundle inventory candidate list as JSONL.

    The JSONL file contains one compact JSON object per inventory candidate,
    using the same filtering and sorting contract as inventory_packet_bundle().
    This is local reporting only. It does not mutate packets, extract archives,
    execute packet contents, call models, contact networks, touch source control,
    validate scientific claims, or promote state.
    """
    inventory = inventory_packet_bundle(
        root,
        recursive=recursive,
        include_zips=include_zips,
        kind_filter=kind_filter,
        status_filter=status_filter,
        sort_by=sort_by,
        reverse=reverse,
    )
    output_path = _validate_jsonl_output_path(output_jsonl, overwrite=overwrite)

    lines = [
        json.dumps(candidate, sort_keys=True, separators=(",", ":"))
        for candidate in inventory["candidates"]
    ]
    output_text = "".join(f"{line}\n" for line in lines)
    output_path.write_text(output_text, encoding="utf-8", newline="\n")

    return {
        "schema_version": "0.1",
        "record_type": PACKET_BUNDLE_INVENTORY_JSONL_EXPORT_RECORD_TYPE,
        "root_path": inventory["root_path"],
        "output_jsonl": str(output_path),
        "export_status": "exported",
        "export_scope": PACKET_BUNDLE_INVENTORY_JSONL_EXPORT_SCOPE,
        "inventory_result_record_type": inventory["record_type"],
        "inventory_status": inventory["inventory_status"],
        "verification_status": inventory["verification_status"],
        "recursive": recursive,
        "include_zips": include_zips,
        "kind_filter": kind_filter,
        "status_filter": status_filter,
        "sort_by": sort_by,
        "sort_reverse": reverse,
        "unfiltered_candidate_count": inventory["unfiltered_candidate_count"],
        "candidate_count": inventory["candidate_count"],
        "packet_dir_count": inventory["packet_dir_count"],
        "packet_zip_count": inventory["packet_zip_count"],
        "failed_candidate_count": inventory["failed_candidate_count"],
        "jsonl_record_count": len(lines),
        "bytes_written": output_path.stat().st_size,
        "overwrite": overwrite,
        "authority_flags": dict(AUTHORITY_FLAGS),
        "authority_note": (
            f"Evidence is not proof. {VERIFICATION_AUTHORITY_NOTE} Packet bundle inventory JSONL export is local reporting only and does "
            "not prove correctness, validate claims, replay execution, touch source control, or promote state."
        ),
        "limitations": list(VERIFICATION_LIMITATIONS)
        + [
            "jsonl_export_does_not_execute_packet_contents",
            "jsonl_export_does_not_validate_scientific_claims",
            "jsonl_export_is_not_import_or_export_authority",
        ],
    }


def _validate_jsonl_output_path(output_jsonl: str | Path, *, overwrite: bool) -> Path:
    output_path = Path(output_jsonl)
    if output_path.exists() and output_path.is_dir():
        raise PacketExportError(f"output JSONL path is a directory: {output_path}")
    if output_path.exists() and not overwrite:
        raise PacketExportError(f"output JSONL already exists: {output_path}")
    if output_path.suffix.lower() != ".jsonl":
        raise PacketExportError(f"output path must end with .jsonl: {output_path}")
    if not output_path.parent.exists():
        raise PacketExportError(f"output directory does not exist: {output_path.parent}")
    return output_path


def _validate_inventory_root(root: str | Path) -> Path:
    root_path = Path(root)
    if not root_path.exists():
        raise PacketInputError(f"inventory root does not exist: {root_path}")
    if not root_path.is_dir():
        raise PacketInputError(f"inventory root is not a directory: {root_path}")
    return root_path


def _validate_inventory_options(kind_filter: str, status_filter: str, sort_by: str) -> None:
    if kind_filter not in INVENTORY_KIND_FILTERS:
        raise PacketInputError(f"unknown inventory kind filter: {kind_filter}")
    if status_filter not in INVENTORY_STATUS_FILTERS:
        raise PacketInputError(f"unknown inventory status filter: {status_filter}")
    if sort_by not in INVENTORY_SORT_FIELDS:
        raise PacketInputError(f"unknown inventory sort field: {sort_by}")


def _packet_dir_candidates(root_path: Path, recursive: bool) -> list[Path]:
    if _looks_like_packet_dir(root_path):
        return [root_path]

    if recursive:
        return sorted(
            path
            for path in root_path.rglob("*")
            if path.is_dir() and _looks_like_packet_dir(path)
        )

    return sorted(
        path
        for path in root_path.iterdir()
        if path.is_dir() and _looks_like_packet_dir(path)
    )


def _packet_zip_candidates(root_path: Path, recursive: bool) -> list[Path]:
    pattern = "**/*.zip" if recursive else "*.zip"
    return sorted(path for path in root_path.glob(pattern) if path.is_file())


def _looks_like_packet_dir(path: Path) -> bool:
    return any((path / name).is_file() for name in REQUIRED_ARTIFACTS)


def _inventory_packet_dir(packet_dir: Path, root_path: Path) -> dict[str, Any]:
    present = sorted(name for name in REQUIRED_ARTIFACTS if (packet_dir / name).is_file())
    missing = sorted(name for name in REQUIRED_ARTIFACTS if name not in present)

    try:
        summary = summarize_packet(packet_dir)
    except EvidenceCoreError as exc:
        return {
            "kind": "packet_dir",
            "path": str(packet_dir),
            "relative_path": _relative_path(packet_dir, root_path),
            "name": packet_dir.name,
            "packet_id": packet_dir.name,
            "inventory_status": "summary_failed",
            "verification_status": "failed_mechanical_checks",
            "present_required_artifact_count": len(present),
            "missing_required_artifact_count": len(missing),
            "present_required_artifacts": present,
            "missing_required_artifacts": missing,
            "error_message": str(exc),
        }

    return {
        "kind": "packet_dir",
        "path": str(packet_dir),
        "relative_path": _relative_path(packet_dir, root_path),
        "name": packet_dir.name,
        "packet_id": summary.get("packet_id") or packet_dir.name,
        "inventory_status": "summarized",
        "verification_status": summary["verification_status"],
        "verification_scope": summary.get("verification_scope"),
        "artifact_count": summary.get("artifact_count"),
        "required_artifact_count": len(REQUIRED_ARTIFACTS),
        "present_required_artifact_count": len(present),
        "missing_required_artifact_count": len(missing),
        "present_required_artifacts": present,
        "missing_required_artifacts": missing,
        "error_count": summary.get("error_count"),
        "warning_count": summary.get("warning_count"),
    }


def _inventory_packet_zip(zip_path: Path, root_path: Path) -> dict[str, Any]:
    try:
        preview = preview_packet_zip(zip_path)
    except EvidenceCoreError as exc:
        return {
            "kind": "packet_zip",
            "path": str(zip_path),
            "relative_path": _relative_path(zip_path, root_path),
            "name": zip_path.name,
            "packet_id": None,
            "inventory_status": "preview_failed",
            "verification_status": "failed_mechanical_checks",
            "preview_status": "preview_error",
            "error_message": str(exc),
        }

    return {
        "kind": "packet_zip",
        "path": str(zip_path),
        "relative_path": _relative_path(zip_path, root_path),
        "name": zip_path.name,
        "packet_id": preview.get("packet_id"),
        "inventory_status": "previewed",
        "verification_status": preview["verification_status"],
        "preview_status": preview["preview_status"],
        "archive_root": preview.get("archive_root"),
        "zip_entry_count": preview.get("zip_entry_count"),
        "missing_required_artifact_count": preview.get("missing_required_artifact_count"),
        "hash_mismatch_count": preview.get("hash_mismatch_count"),
        "unsafe_entry_count": preview.get("unsafe_entry_count"),
    }


def _filter_candidates(
    candidates: list[dict[str, Any]],
    *,
    kind_filter: str,
    status_filter: str,
) -> list[dict[str, Any]]:
    return [
        candidate
        for candidate in candidates
        if _matches_kind_filter(candidate, kind_filter)
        and _matches_status_filter(candidate, status_filter)
    ]


def _matches_kind_filter(candidate: dict[str, Any], kind_filter: str) -> bool:
    if kind_filter == "all":
        return True
    if kind_filter == "dirs":
        return candidate.get("kind") == "packet_dir"
    if kind_filter == "zips":
        return candidate.get("kind") == "packet_zip"
    return False


def _matches_status_filter(candidate: dict[str, Any], status_filter: str) -> bool:
    verification_status = candidate.get("verification_status")
    if status_filter == "all":
        return True
    if status_filter == "passed":
        return verification_status == "passed_mechanical_checks"
    if status_filter == "failed":
        return verification_status != "passed_mechanical_checks"
    return False


def _sort_candidates(
    candidates: list[dict[str, Any]],
    *,
    sort_by: str,
    reverse: bool,
) -> list[dict[str, Any]]:
    return sorted(
        candidates,
        key=lambda candidate: _sort_key(candidate, sort_by),
        reverse=reverse,
    )


def _sort_key(candidate: dict[str, Any], sort_by: str) -> tuple[str, str, str]:
    if sort_by == "name":
        return (str(candidate.get("name") or ""), str(candidate.get("relative_path") or ""), str(candidate.get("kind") or ""))
    if sort_by == "kind":
        return (str(candidate.get("kind") or ""), str(candidate.get("relative_path") or ""), str(candidate.get("name") or ""))
    if sort_by == "verification-status":
        return (str(candidate.get("verification_status") or ""), str(candidate.get("relative_path") or ""), str(candidate.get("kind") or ""))
    return (str(candidate.get("relative_path") or ""), str(candidate.get("kind") or ""), str(candidate.get("name") or ""))


def _relative_path(path: Path, root_path: Path) -> str:
    try:
        relative = path.relative_to(root_path)
    except ValueError:
        return str(path)
    return "." if str(relative) == "." else relative.as_posix()
