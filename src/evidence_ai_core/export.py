from __future__ import annotations

from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile

from .constants import AUTHORITY_FLAGS, VERIFICATION_AUTHORITY_NOTE, VERIFICATION_LIMITATIONS
from .errors import PacketExportError, PacketInputError
from .verify import verify_packet


PACKET_ZIP_EXPORT_RESULT_RECORD_TYPE = "packet_zip_export_result"
PACKET_ZIP_EXPORT_SCOPE = "static_packet_archive_only"


def export_packet_zip(
    packet_dir: str | Path,
    output_zip: str | Path,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Export an existing static packet directory to a deterministic ZIP archive.

    This is a local file-packaging operation only. It does not execute packet
    contents, call models, run notebooks, contact networks, mutate source
    control, validate scientific claims, or promote state.
    """
    packet_path = _validate_packet_dir(packet_dir)
    output_path = Path(output_zip)

    if output_path.exists() and output_path.is_dir():
        raise PacketExportError(f"output ZIP path is a directory: {output_path}")
    if output_path.exists() and not overwrite:
        raise PacketExportError(f"output ZIP already exists: {output_path}")
    if output_path.suffix.lower() != ".zip":
        raise PacketExportError(f"output path must end with .zip: {output_path}")
    if not output_path.parent.exists():
        raise PacketExportError(f"output directory does not exist: {output_path.parent}")

    resolved_packet = packet_path.resolve()
    resolved_output = output_path.resolve()
    if _is_relative_to(resolved_output, resolved_packet):
        raise PacketExportError("output ZIP must not be written inside the packet directory")

    entries = _packet_file_entries(packet_path)
    if not entries:
        raise PacketExportError(f"packet directory contains no files: {packet_path}")

    verification = verify_packet(packet_path)
    archive_root = packet_path.name

    with ZipFile(output_path, "w", compression=ZIP_DEFLATED) as archive:
        for rel_path in entries:
            source_path = packet_path / rel_path
            archive.write(source_path, arcname=f"{archive_root}/{rel_path.as_posix()}")

    exported_entries = [f"{archive_root}/{rel_path.as_posix()}" for rel_path in entries]

    return {
        "schema_version": "0.1",
        "record_type": PACKET_ZIP_EXPORT_RESULT_RECORD_TYPE,
        "packet_id": verification.get("packet_id") or packet_path.name,
        "packet_dir": str(packet_path),
        "output_zip": str(output_path),
        "export_status": "exported",
        "export_scope": PACKET_ZIP_EXPORT_SCOPE,
        "archive_format": "zip",
        "archive_root": archive_root,
        "compression": "zip_deflated",
        "file_count": len(entries),
        "zip_entry_count": len(exported_entries),
        "zip_entries": exported_entries,
        "bytes_written": output_path.stat().st_size,
        "verification_status": verification["verification_status"],
        "verification_scope": verification.get("verification_scope"),
        "authority_flags": dict(AUTHORITY_FLAGS),
        "authority_note": (
            f"{VERIFICATION_AUTHORITY_NOTE} ZIP export is local file packaging only and does "
            "not prove correctness, validate claims, replay execution, touch source control, or promote state."
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


def _packet_file_entries(packet_path: Path) -> list[Path]:
    return sorted(
        path.relative_to(packet_path)
        for path in packet_path.rglob("*")
        if path.is_file()
    )


def _is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True
