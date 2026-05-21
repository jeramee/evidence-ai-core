import json
from pathlib import Path
from zipfile import ZipFile

import pytest

from evidence_ai_core import create_static_packet, export_packet_zip, extract_packet_zip, preview_packet_zip
from evidence_ai_core.errors import PacketImportError, PacketInputError


def make_packet_zip(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path / "source.md"
    source.write_text("# Source\nEvidence text.", encoding="utf-8")
    packet_dir = create_static_packet("import preview request", [str(source)], tmp_path / "packets")
    output_zip = tmp_path / "packet.zip"
    export_packet_zip(packet_dir, output_zip)
    return packet_dir, output_zip


def test_preview_packet_zip_returns_static_import_preview_contract(tmp_path):
    packet_dir, output_zip = make_packet_zip(tmp_path)

    result = preview_packet_zip(output_zip)

    assert result["schema_version"] == "0.1"
    assert result["record_type"] == "packet_zip_import_preview_result"
    assert result["packet_id"] == packet_dir.name
    assert result["zip_path"] == str(output_zip)
    assert result["preview_status"] == "previewed"
    assert result["import_status"] == "not_imported_preview_only"
    assert result["verification_status"] == "passed_mechanical_checks"
    assert result["verification_scope"] == "static_zip_preview_only_no_extraction"
    assert result["archive_format"] == "zip"
    assert result["archive_root"] == packet_dir.name
    assert result["zip_entry_count"] == 8
    assert result["required_artifact_count"] == 8
    assert result["present_required_artifact_count"] == 8
    assert result["missing_required_artifact_count"] == 0
    assert result["missing_required_artifacts"] == []
    assert result["json_record_count"] == 7
    assert result["packet_id_count"] == 1
    assert result["record_type_error_count"] == 0
    assert result["declared_artifact_count"] == 8
    assert result["hash_algorithm"] == "sha256"
    assert result["hash_mismatch_count"] == 0
    assert result["missing_declared_artifact_count"] == 0
    assert result["malformed_manifest_entry_count"] == 0
    assert result["extraction_performed"] is False
    assert result["unsafe_entry_count"] == 0
    assert result["authority_flags"] == {
        "correctness_proven": False,
        "repo_mutated": False,
        "state_promoted": False,
        "source_control_touched": False,
    }
    assert "does not extract" in result["authority_note"]
    assert "scientific validation" in result["authority_note"]
    assert any(artifact["path"] == "context_pack.md" for artifact in result["artifacts"])


def test_preview_packet_zip_does_not_extract_files(tmp_path):
    _packet_dir, output_zip = make_packet_zip(tmp_path)
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*") if path.is_file())

    result = preview_packet_zip(output_zip)

    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*") if path.is_file())
    assert result["extraction_performed"] is False
    assert after == before


def test_preview_packet_zip_reports_missing_required_artifact(tmp_path):
    packet_dir, _output_zip = make_packet_zip(tmp_path)
    incomplete_zip = tmp_path / "incomplete.zip"

    with ZipFile(incomplete_zip, "w") as archive:
        for path in sorted(packet_dir.iterdir()):
            if path.name == "retrieval_record.json":
                continue
            archive.write(path, arcname=f"{packet_dir.name}/{path.name}")

    result = preview_packet_zip(incomplete_zip)

    assert result["preview_status"] == "preview_failed"
    assert result["verification_status"] == "failed_mechanical_checks"
    assert result["missing_required_artifact_count"] == 1
    assert result["missing_required_artifacts"] == ["retrieval_record.json"]


def test_preview_packet_zip_detects_hash_mismatch_inside_archive(tmp_path):
    packet_dir, _output_zip = make_packet_zip(tmp_path)
    tampered_zip = tmp_path / "tampered.zip"

    with ZipFile(tampered_zip, "w") as archive:
        for path in sorted(packet_dir.iterdir()):
            arcname = f"{packet_dir.name}/{path.name}"
            if path.name == "context_pack.md":
                archive.writestr(arcname, "tampered context\n")
            else:
                archive.write(path, arcname=arcname)

    result = preview_packet_zip(tampered_zip)

    assert result["preview_status"] == "preview_failed"
    assert result["verification_status"] == "failed_mechanical_checks"
    assert result["hash_mismatch_count"] == 1
    assert any(
        artifact["path"] == "context_pack.md" and artifact["hash_status"] == "hash_mismatch"
        for artifact in result["artifacts"]
    )


def test_preview_packet_zip_rejects_unsafe_zip_entries(tmp_path):
    unsafe_zip = tmp_path / "unsafe.zip"
    with ZipFile(unsafe_zip, "w") as archive:
        archive.writestr("../evil.txt", "bad")

    with pytest.raises(PacketImportError, match="unsafe ZIP entry"):
        preview_packet_zip(unsafe_zip)


def test_preview_packet_zip_rejects_missing_zip(tmp_path):
    with pytest.raises(PacketInputError, match="ZIP file does not exist"):
        preview_packet_zip(tmp_path / "missing.zip")


def test_preview_packet_zip_rejects_invalid_json(tmp_path):
    packet_dir, _output_zip = make_packet_zip(tmp_path)
    invalid_zip = tmp_path / "invalid-json.zip"

    with ZipFile(invalid_zip, "w") as archive:
        for path in sorted(packet_dir.iterdir()):
            arcname = f"{packet_dir.name}/{path.name}"
            if path.name == "query_job.json":
                archive.writestr(arcname, "{not valid json")
            else:
                archive.write(path, arcname=arcname)

    with pytest.raises(PacketImportError, match="invalid JSON in ZIP"):
        preview_packet_zip(invalid_zip)



def test_extract_packet_zip_safely_extracts_valid_packet_archive(tmp_path):
    packet_dir, output_zip = make_packet_zip(tmp_path)
    output_root = tmp_path / "imports"
    output_root.mkdir()

    result = extract_packet_zip(output_zip, output_root)
    extracted_packet = output_root / packet_dir.name

    assert result["schema_version"] == "0.1"
    assert result["record_type"] == "packet_zip_import_result"
    assert result["packet_id"] == packet_dir.name
    assert result["zip_path"] == str(output_zip)
    assert result["output_root"] == str(output_root)
    assert result["extracted_packet_dir"] == str(extracted_packet)
    assert result["import_status"] == "imported"
    assert result["extraction_status"] == "extracted"
    assert result["import_scope"] == "static_zip_safe_extract_only"
    assert result["preview_status"] == "previewed"
    assert result["verification_status"] == "passed_mechanical_checks"
    assert result["extraction_performed"] is True
    assert result["extracted_file_count"] == 8
    assert result["zip_entry_count"] == 8
    assert result["overwrite"] is False
    assert extracted_packet.exists()
    assert (extracted_packet / "context_pack.md").read_bytes() == (packet_dir / "context_pack.md").read_bytes()
    assert "does not prove correctness" in result["authority_note"]


def test_extract_packet_zip_refuses_existing_destination_without_overwrite(tmp_path):
    packet_dir, output_zip = make_packet_zip(tmp_path)
    output_root = tmp_path / "imports"
    output_root.mkdir()
    (output_root / packet_dir.name).mkdir()

    with pytest.raises(PacketImportError, match="already exists"):
        extract_packet_zip(output_zip, output_root)


def test_extract_packet_zip_supports_explicit_overwrite(tmp_path):
    packet_dir, output_zip = make_packet_zip(tmp_path)
    output_root = tmp_path / "imports"
    output_root.mkdir()

    first = extract_packet_zip(output_zip, output_root)
    marker = Path(first["extracted_packet_dir"]) / "old.txt"
    marker.write_text("old", encoding="utf-8")

    second = extract_packet_zip(output_zip, output_root, overwrite=True)

    assert second["overwrite"] is True
    assert not marker.exists()
    assert Path(second["extracted_packet_dir"]).exists()


def test_extract_packet_zip_refuses_failed_preview_without_extracting(tmp_path):
    packet_dir, _output_zip = make_packet_zip(tmp_path)
    tampered_zip = tmp_path / "tampered.zip"
    output_root = tmp_path / "imports"
    output_root.mkdir()

    with ZipFile(tampered_zip, "w") as archive:
        for path in sorted(packet_dir.iterdir()):
            arcname = f"{packet_dir.name}/{path.name}"
            if path.name == "context_pack.md":
                archive.writestr(arcname, "tampered context\n")
            else:
                archive.write(path, arcname=arcname)

    with pytest.raises(PacketImportError, match="preview failed"):
        extract_packet_zip(tampered_zip, output_root)

    assert not (output_root / packet_dir.name).exists()


def test_extract_packet_zip_rejects_unsafe_zip_entries_without_extracting(tmp_path):
    unsafe_zip = tmp_path / "unsafe.zip"
    output_root = tmp_path / "imports"
    output_root.mkdir()

    with ZipFile(unsafe_zip, "w") as archive:
        archive.writestr("../evil.txt", "bad")

    with pytest.raises(PacketImportError, match="unsafe ZIP entry"):
        extract_packet_zip(unsafe_zip, output_root)

    assert list(output_root.iterdir()) == []
