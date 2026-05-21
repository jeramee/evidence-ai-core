from pathlib import Path
from zipfile import ZipFile

from evidence_ai_core import (
    create_static_packet,
    export_packet_zip,
    extract_packet_zip,
    load_packet,
    preview_packet_zip,
    summarize_artifact_hashes,
    summarize_packet,
    verify_packet,
)
from evidence_ai_core.constants import REQUIRED_ARTIFACTS


def make_roundtrip(tmp_path: Path) -> tuple[Path, Path, dict, dict, Path]:
    source = tmp_path / "source.md"
    source.write_text("# Source\nEvidence text.", encoding="utf-8")
    original_packet = create_static_packet("roundtrip request", [str(source)], tmp_path / "packets")

    export_root = tmp_path / "exports"
    export_root.mkdir()
    packet_zip = export_root / "packet.zip"
    export_result = export_packet_zip(original_packet, packet_zip)

    import_root = tmp_path / "imports"
    import_root.mkdir()
    import_result = extract_packet_zip(packet_zip, import_root)
    extracted_packet = Path(import_result["extracted_packet_dir"])

    return original_packet, packet_zip, export_result, import_result, extracted_packet


def test_static_packet_zip_roundtrip_preserves_packet_identity_and_artifacts(tmp_path):
    original_packet, packet_zip, export_result, import_result, extracted_packet = make_roundtrip(tmp_path)

    preview_result = preview_packet_zip(packet_zip)
    extracted_verification = verify_packet(extracted_packet)
    extracted_loaded = load_packet(extracted_packet)
    extracted_summary = summarize_packet(extracted_packet)

    assert export_result["record_type"] == "packet_zip_export_result"
    assert preview_result["record_type"] == "packet_zip_import_preview_result"
    assert import_result["record_type"] == "packet_zip_import_result"
    assert export_result["packet_id"] == original_packet.name
    assert preview_result["packet_id"] == original_packet.name
    assert import_result["packet_id"] == original_packet.name
    assert extracted_verification["packet_id"] == original_packet.name
    assert extracted_loaded["packet_id"] == original_packet.name
    assert extracted_summary["packet_id"] == original_packet.name
    assert extracted_packet.name == original_packet.name
    assert extracted_packet != original_packet

    for artifact_name in REQUIRED_ARTIFACTS:
        assert (extracted_packet / artifact_name).read_bytes() == (original_packet / artifact_name).read_bytes()


def test_static_packet_zip_roundtrip_keeps_mechanical_statuses_green(tmp_path):
    _original_packet, packet_zip, export_result, import_result, extracted_packet = make_roundtrip(tmp_path)

    preview_result = preview_packet_zip(packet_zip)
    verification_result = verify_packet(extracted_packet)
    loaded_result = load_packet(extracted_packet)
    summary_result = summarize_packet(extracted_packet)
    hash_summary = summarize_artifact_hashes(extracted_packet)

    assert export_result["verification_status"] == "passed_mechanical_checks"
    assert preview_result["verification_status"] == "passed_mechanical_checks"
    assert import_result["verification_status"] == "passed_mechanical_checks"
    assert verification_result["verification_status"] == "passed_mechanical_checks"
    assert loaded_result["verification_status"] == "passed_mechanical_checks"
    assert summary_result["verification_status"] == "passed_mechanical_checks"
    assert hash_summary["verification_status"] == "passed_mechanical_checks"
    assert hash_summary["hash_mismatch_count"] == 0
    assert hash_summary["missing_artifact_count"] == 0


def test_static_packet_zip_roundtrip_archive_root_and_counts_stay_consistent(tmp_path):
    original_packet, packet_zip, export_result, import_result, extracted_packet = make_roundtrip(tmp_path)
    preview_result = preview_packet_zip(packet_zip)

    with ZipFile(packet_zip) as archive:
        zip_entries = sorted(archive.namelist())

    assert export_result["archive_root"] == original_packet.name
    assert preview_result["archive_root"] == original_packet.name
    assert import_result["archive_root"] == original_packet.name
    assert export_result["zip_entry_count"] == len(REQUIRED_ARTIFACTS)
    assert preview_result["zip_entry_count"] == len(REQUIRED_ARTIFACTS)
    assert import_result["zip_entry_count"] == len(REQUIRED_ARTIFACTS)
    assert import_result["extracted_file_count"] == len(REQUIRED_ARTIFACTS)
    assert zip_entries == export_result["zip_entries"]
    assert sorted(import_result["extracted_files"]) == sorted(REQUIRED_ARTIFACTS)
    assert sorted(path.name for path in extracted_packet.iterdir() if path.is_file()) == sorted(REQUIRED_ARTIFACTS)
