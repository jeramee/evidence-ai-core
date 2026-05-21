from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any
from zipfile import ZipFile

from .constants import AUTHORITY_FLAGS, VERIFICATION_AUTHORITY_NOTE, VERIFICATION_LIMITATIONS
from .errors import PacketImportError, PacketInputError
from .import_preview import (
    _is_safe_zip_entry,
    _single_archive_root,
    _strip_archive_root,
    _validate_zip_path,
    preview_packet_zip,
)
from .verify import verify_packet


PACKET_ZIP_IMPORT_EXTRACT_RESULT_RECORD_TYPE = "packet_zip_import_result"
PACKET_ZIP_IMPORT_EXTRACT_SCOPE = "static_zip_safe_extract_only"


def extract_packet_zip(
    zip_path: str | Path,
    output_root: str | Path,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Safely extract a previously exported static packet ZIP.

    Extraction is local file copying only. The ZIP is previewed first and must
    pass mechanical import-preview checks before any files are written. This API
    does not execute packet contents, call models, run notebooks, contact
    networks, mutate source control, validate scientific claims, or promote
    state.
    """
    archive_path = _validate_zip_path(zip_path)
    destination_root = _validate_output_root(output_root)
    preview = preview_packet_zip(archive_path)

    if preview["verification_status"] != "passed_mechanical_checks":
        raise PacketImportError("ZIP preview failed; refusing extraction")

    archive_root = preview["archive_root"]
    destination_packet_dir = destination_root / archive_root

    if destination_packet_dir.exists() and not overwrite:
        raise PacketImportError(f"destination packet directory already exists: {destination_packet_dir}")
    if destination_packet_dir.exists() and not destination_packet_dir.is_dir():
        raise PacketImportError(f"destination packet path is not a directory: {destination_packet_dir}")

    if destination_packet_dir.exists() and overwrite:
        shutil.rmtree(destination_packet_dir)

    extracted_files: list[str] = []
    bytes_written = 0

    with ZipFile(archive_path) as archive:
        infos = [info for info in archive.infolist() if not info.is_dir()]
        entry_names = [info.filename for info in infos]
        unsafe_entries = [name for name in entry_names if not _is_safe_zip_entry(name)]
        if unsafe_entries:
            raise PacketImportError(f"unsafe ZIP entry detected: {unsafe_entries[0]}")

        confirmed_root = _single_archive_root(entry_names)
        if confirmed_root != archive_root:
            raise PacketImportError("ZIP archive root changed between preview and extraction")

        destination_root_resolved = destination_root.resolve()
        destination_packet_resolved = destination_packet_dir.resolve()

        for info in infos:
            rel_path = _strip_archive_root(info.filename, archive_root)
            destination = destination_packet_dir / Path(rel_path)
            destination_resolved = destination.resolve()

            if not _is_relative_to(destination_resolved, destination_root_resolved):
                raise PacketImportError(f"unsafe extraction target outside output root: {info.filename}")
            if not _is_relative_to(destination_resolved, destination_packet_resolved):
                raise PacketImportError(f"unsafe extraction target outside packet directory: {info.filename}")

            destination.parent.mkdir(parents=True, exist_ok=True)
            data = archive.read(info.filename)
            destination.write_bytes(data)
            bytes_written += len(data)
            extracted_files.append(rel_path)

    verification = verify_packet(destination_packet_dir)

    return {
        "schema_version": "0.1",
        "record_type": PACKET_ZIP_IMPORT_EXTRACT_RESULT_RECORD_TYPE,
        "packet_id": verification.get("packet_id") or preview.get("packet_id"),
        "zip_path": str(archive_path),
        "output_root": str(destination_root),
        "extracted_packet_dir": str(destination_packet_dir),
        "import_status": "imported",
        "extraction_status": "extracted",
        "import_scope": PACKET_ZIP_IMPORT_EXTRACT_SCOPE,
        "preview_status": preview["preview_status"],
        "archive_format": "zip",
        "archive_root": archive_root,
        "zip_entry_count": preview["zip_entry_count"],
        "file_count": len(extracted_files),
        "extracted_file_count": len(extracted_files),
        "extracted_files": sorted(extracted_files),
        "bytes_written": bytes_written,
        "overwrite": overwrite,
        "extraction_performed": True,
        "verification_status": verification["verification_status"],
        "verification_scope": verification.get("verification_scope"),
        "preview_result_record_type": preview["record_type"],
        "unsafe_entry_count": 0,
        "authority_flags": dict(AUTHORITY_FLAGS),
        "authority_note": (
            f"{VERIFICATION_AUTHORITY_NOTE} ZIP import extraction is local file copying only and does "
            "not prove correctness, validate claims, replay execution, touch source control, or promote state."
        ),
        "limitations": list(VERIFICATION_LIMITATIONS) + [
            "does_not_execute_imported_packet_contents",
            "does_not_validate_scientific_claims",
            "requires_preview_to_pass_before_extraction",
        ],
    }


def _validate_output_root(output_root: str | Path) -> Path:
    root = Path(output_root)
    if not root.exists():
        raise PacketInputError(f"output root does not exist: {root}")
    if not root.is_dir():
        raise PacketInputError(f"output root is not a directory: {root}")
    return root


def _is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True
