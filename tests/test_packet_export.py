import json
from pathlib import Path
from zipfile import ZipFile

import pytest

from evidence_ai_core import create_static_packet, export_packet_zip
from evidence_ai_core.errors import PacketExportError, PacketInputError


def make_packet(tmp_path: Path) -> Path:
    source = tmp_path / "source.md"
    source.write_text("# Source\nEvidence text.", encoding="utf-8")
    return create_static_packet("export request", [str(source)], tmp_path / "packets")


def test_export_packet_zip_creates_static_archive_contract(tmp_path):
    packet_dir = make_packet(tmp_path)
    output_zip = tmp_path / "exports" / "packet.zip"
    output_zip.parent.mkdir()

    result = export_packet_zip(packet_dir, output_zip)

    assert result["schema_version"] == "0.1"
    assert result["record_type"] == "packet_zip_export_result"
    assert result["packet_id"] == packet_dir.name
    assert result["packet_dir"] == str(packet_dir)
    assert result["output_zip"] == str(output_zip)
    assert result["export_status"] == "exported"
    assert result["export_scope"] == "static_packet_archive_only"
    assert result["archive_format"] == "zip"
    assert result["archive_root"] == packet_dir.name
    assert result["compression"] == "zip_deflated"
    assert result["verification_status"] == "passed_mechanical_checks"
    assert result["file_count"] == 8
    assert result["zip_entry_count"] == 8
    assert result["bytes_written"] > 0
    assert result["authority_flags"] == {
        "correctness_proven": False,
        "repo_mutated": False,
        "state_promoted": False,
        "source_control_touched": False,
    }
    assert "scientific validation" in result["authority_note"]
    assert output_zip.exists()

    with ZipFile(output_zip) as archive:
        names = sorted(archive.namelist())

    assert names == sorted(result["zip_entries"])
    assert names == [
        f"{packet_dir.name}/artifact_manifest.json",
        f"{packet_dir.name}/context_pack.md",
        f"{packet_dir.name}/environment_report.json",
        f"{packet_dir.name}/notebook_run_record.json",
        f"{packet_dir.name}/query_job.json",
        f"{packet_dir.name}/replay_manifest.json",
        f"{packet_dir.name}/retrieval_record.json",
        f"{packet_dir.name}/source_citations.json",
    ]


def test_export_packet_zip_preserves_file_contents(tmp_path):
    packet_dir = make_packet(tmp_path)
    output_zip = tmp_path / "packet.zip"

    export_packet_zip(packet_dir, output_zip)

    with ZipFile(output_zip) as archive:
        archived_context = archive.read(f"{packet_dir.name}/context_pack.md")

    assert archived_context == (packet_dir / "context_pack.md").read_bytes()


def test_export_packet_zip_refuses_overwrite_by_default(tmp_path):
    packet_dir = make_packet(tmp_path)
    output_zip = tmp_path / "packet.zip"

    export_packet_zip(packet_dir, output_zip)

    with pytest.raises(PacketExportError, match="already exists"):
        export_packet_zip(packet_dir, output_zip)


def test_export_packet_zip_can_overwrite_explicitly(tmp_path):
    packet_dir = make_packet(tmp_path)
    output_zip = tmp_path / "packet.zip"

    export_packet_zip(packet_dir, output_zip)
    first_size = output_zip.stat().st_size
    result = export_packet_zip(packet_dir, output_zip, overwrite=True)

    assert result["bytes_written"] == output_zip.stat().st_size
    assert output_zip.stat().st_size == first_size


def test_export_packet_zip_rejects_output_inside_packet_dir(tmp_path):
    packet_dir = make_packet(tmp_path)

    with pytest.raises(PacketExportError, match="inside the packet directory"):
        export_packet_zip(packet_dir, packet_dir / "packet.zip")


def test_export_packet_zip_rejects_missing_packet_dir(tmp_path):
    with pytest.raises(PacketInputError, match="packet directory does not exist"):
        export_packet_zip(tmp_path / "missing", tmp_path / "packet.zip")


def test_export_packet_zip_reports_failed_mechanical_status_for_tampered_packet(tmp_path):
    packet_dir = make_packet(tmp_path)
    output_zip = tmp_path / "packet.zip"
    (packet_dir / "context_pack.md").write_text("tampered context\n", encoding="utf-8")

    result = export_packet_zip(packet_dir, output_zip)

    assert result["export_status"] == "exported"
    assert result["verification_status"] == "failed_mechanical_checks"
    assert output_zip.exists()
