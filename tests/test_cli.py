import json
import socket
import subprocess
from pathlib import Path

from evidence_ai_core.cli import main


FORBIDDEN_AUTHORITY_WORDS = (
    "correctness proven",
    "scientifically validated",
    "validated science",
    "state promoted",
    "replay proven",
)


def make_source(tmp_path: Path) -> Path:
    source = tmp_path / "source.md"
    source.write_text("# Source\nEvidence text.", encoding="utf-8")
    return source


def create_packet_with_cli(tmp_path: Path, capsys, request_text: str = "cli smoke request") -> Path:
    source = make_source(tmp_path)
    output_root = tmp_path / "packets"

    status = main(
        [
            "create-static",
            "--request-text",
            request_text,
            "--source",
            str(source),
            "--output-root",
            str(output_root),
        ]
    )
    packet_dir = Path(capsys.readouterr().out.strip())

    assert status == 0
    assert packet_dir.exists()
    return packet_dir


def test_cli_create_static_verify_and_inspect_smoke(tmp_path, capsys):
    source = make_source(tmp_path)
    output_root = tmp_path / "packets"

    create_status = main(
        [
            "create-static",
            "--request-text",
            "cli smoke request",
            "--source",
            str(source),
            "--output-root",
            str(output_root),
        ]
    )

    create_out = capsys.readouterr().out.strip()
    packet_dir = Path(create_out)

    assert create_status == 0
    assert packet_dir.exists()
    assert packet_dir.parent == output_root
    assert (packet_dir / "query_job.json").exists()

    verify_status = main(["verify", str(packet_dir)])
    verify_result = json.loads(capsys.readouterr().out)

    assert verify_status == 0
    assert verify_result["verification_status"] == "passed_mechanical_checks"
    assert verify_result["packet_id"] == packet_dir.name

    inspect_status = main(["inspect", str(packet_dir)])
    inspect_result = json.loads(capsys.readouterr().out)

    assert inspect_status == 0
    assert inspect_result["record_type"] == "packet_inspection_summary"
    assert inspect_result["verification_status"] == "passed_mechanical_checks"


def test_cli_inspect_emits_readonly_summary(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)

    inspect_status = main(["inspect", str(packet_dir)])
    summary = json.loads(capsys.readouterr().out)

    assert inspect_status == 0
    assert summary["record_type"] == "packet_inspection_summary"
    assert summary["packet_id"] == packet_dir.name
    assert summary["verification_status"] == "passed_mechanical_checks"
    assert {item["path"] for item in summary["required_artifacts"]} >= {
        "query_job.json",
        "retrieval_record.json",
        "source_citations.json",
        "context_pack.md",
        "notebook_run_record.json",
        "environment_report.json",
        "artifact_manifest.json",
        "replay_manifest.json",
    }
    assert summary["authority_flags"] == {
        "correctness_proven": False,
        "repo_mutated": False,
        "state_promoted": False,
        "source_control_touched": False,
    }
    assert "Evidence is not proof" in summary["authority_note"]


def test_cli_inspect_does_not_modify_packet_directory(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)
    before = sorted((path.name, path.stat().st_mtime_ns) for path in packet_dir.iterdir())

    status = main(["inspect", str(packet_dir)])
    capsys.readouterr()

    after = sorted((path.name, path.stat().st_mtime_ns) for path in packet_dir.iterdir())
    assert status == 0
    assert after == before


def test_cli_inspect_does_not_claim_validation_or_proof(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)

    status = main(["inspect", str(packet_dir)])
    output = capsys.readouterr().out.lower()

    assert status == 0
    for forbidden in FORBIDDEN_AUTHORITY_WORDS:
        assert forbidden not in output



def test_cli_summary_emits_stable_compact_shape(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)

    status = main(["summary", str(packet_dir)])
    summary = json.loads(capsys.readouterr().out)

    assert status == 0
    assert summary["schema_version"] == "0.1"
    assert summary["record_type"] == "packet_summary"
    assert summary["packet_id"] == packet_dir.name
    assert summary["verification_status"] == "passed_mechanical_checks"
    assert summary["verification_scope"] == "mechanical_packet_shape_only"
    assert summary["artifact_count"] == 8
    assert summary["required_artifact_count"] == 8
    assert summary["missing_artifact_count"] == 0
    assert summary["json_record_count"] == 7
    assert summary["text_artifact_count"] == 1
    assert summary["error_count"] == 0
    assert "artifacts" in summary
    assert {artifact["path"] for artifact in summary["artifacts"]} >= {
        "query_job.json",
        "retrieval_record.json",
        "context_pack.md",
    }
    assert "json_records" not in summary
    assert "text_artifacts" not in summary
    assert "verification_result" not in summary
    assert "Evidence is not proof" in summary["authority_note"]


def test_cli_summary_returns_nonzero_for_failed_packet(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)
    (packet_dir / "retrieval_record.json").unlink()

    status = main(["summary", str(packet_dir)])
    summary = json.loads(capsys.readouterr().out)

    assert status != 0
    assert summary["verification_status"] == "failed_mechanical_checks"
    assert summary["missing_artifact_count"] == 1
    assert any(artifact["path"] == "retrieval_record.json" and not artifact["exists"] for artifact in summary["artifacts"])


def test_cli_create_static_accepts_request_file(tmp_path, capsys):
    request_file = tmp_path / "request.txt"
    request_file.write_text("request from file", encoding="utf-8")
    source = make_source(tmp_path)
    output_root = tmp_path / "packets"

    status = main(
        [
            "create-static",
            "--request-file",
            str(request_file),
            "--source",
            str(source),
            "--output-root",
            str(output_root),
        ]
    )

    packet_dir = Path(capsys.readouterr().out.strip())
    query_job = json.loads((packet_dir / "query_job.json").read_text(encoding="utf-8"))

    assert status == 0
    assert query_job["request_text"] == "request from file"


def test_cli_create_static_returns_nonzero_for_missing_request_file(tmp_path, capsys):
    source = make_source(tmp_path)
    missing_request = tmp_path / "missing-request.txt"

    status = main(
        [
            "create-static",
            "--request-file",
            str(missing_request),
            "--source",
            str(source),
            "--output-root",
            str(tmp_path / "packets"),
        ]
    )
    captured = capsys.readouterr()

    assert status != 0
    assert "request file does not exist" in captured.err


def test_cli_create_static_rejects_ambiguous_request_text_and_file(tmp_path, capsys):
    request_file = tmp_path / "request.txt"
    request_file.write_text("request from file", encoding="utf-8")
    source = make_source(tmp_path)

    status = main(
        [
            "create-static",
            "--request-text",
            "direct request",
            "--request-file",
            str(request_file),
            "--source",
            str(source),
            "--output-root",
            str(tmp_path / "packets"),
        ]
    )
    captured = capsys.readouterr()

    assert status != 0
    assert "not allowed with argument" in captured.err


def test_cli_verify_returns_zero_for_valid_packet(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)

    status = main(["verify", str(packet_dir)])
    result = json.loads(capsys.readouterr().out)

    assert status == 0
    assert result["verification_status"] == "passed_mechanical_checks"


def test_cli_verify_returns_nonzero_for_failed_packet(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)
    (packet_dir / "retrieval_record.json").unlink()

    status = main(["verify", str(packet_dir)])
    result = json.loads(capsys.readouterr().out)

    assert status != 0
    assert result["verification_status"] == "failed_mechanical_checks"
    assert "retrieval_record.json" in result["errors"]


def test_cli_verify_missing_packet_dir_returns_nonzero(tmp_path, capsys):
    missing_packet = tmp_path / "missing-packet"

    status = main(["verify", str(missing_packet)])
    captured = capsys.readouterr()

    assert status != 0
    assert "packet directory does not exist" in captured.err


def test_cli_create_static_missing_source_returns_nonzero(tmp_path, capsys):
    missing_source = tmp_path / "missing-source.md"

    status = main(
        [
            "create-static",
            "--request-text",
            "request",
            "--source",
            str(missing_source),
            "--output-root",
            str(tmp_path / "packets"),
        ]
    )
    captured = capsys.readouterr()

    assert status != 0
    assert "source file does not exist" in captured.err


def test_cli_error_text_is_clear_without_being_brittle(tmp_path, capsys):
    status = main(["verify", str(tmp_path / "not-a-packet")])
    captured = capsys.readouterr()

    assert status != 0
    assert "error:" in captured.err
    assert "does not exist" in captured.err


def test_cli_main_does_not_require_external_actions(tmp_path, monkeypatch, capsys):
    def fail_network(*args, **kwargs):
        raise AssertionError("network calls are forbidden for evidence-ai-core CLI smoke")

    def fail_subprocess(*args, **kwargs):
        raise AssertionError("subprocess calls are forbidden for evidence-ai-core CLI smoke")

    monkeypatch.setattr(socket, "socket", fail_network)
    monkeypatch.setattr(subprocess, "run", fail_subprocess)

    source = make_source(tmp_path)
    output_root = tmp_path / "packets"

    create_status = main(
        [
            "create-static",
            "--request-text",
            "cli no external action request",
            "--source",
            str(source),
            "--output-root",
            str(output_root),
        ]
    )
    packet_dir = Path(capsys.readouterr().out.strip())

    verify_status = main(["verify", str(packet_dir)])
    verify_result = json.loads(capsys.readouterr().out)

    inspect_status = main(["inspect", str(packet_dir)])
    inspect_result = json.loads(capsys.readouterr().out)

    summary_status = main(["summary", str(packet_dir)])
    summary_result = json.loads(capsys.readouterr().out)

    manifest_status = main(["manifest", str(packet_dir)])
    manifest_result = json.loads(capsys.readouterr().out)

    hash_summary_status = main(["hash-summary", str(packet_dir)])
    hash_summary_result = json.loads(capsys.readouterr().out)

    assert create_status == 0
    assert verify_status == 0
    assert inspect_status == 0
    assert summary_status == 0
    assert manifest_status == 0
    assert hash_summary_status == 0
    assert verify_result["verification_status"] == "passed_mechanical_checks"
    assert inspect_result["verification_status"] == "passed_mechanical_checks"
    assert summary_result["verification_status"] == "passed_mechanical_checks"
    assert manifest_result["record_type"] == "artifact_manifest_read_result"
    assert hash_summary_result["verification_status"] == "passed_mechanical_checks"


def test_cli_manifest_emits_readonly_artifact_manifest_result(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)

    status = main(["manifest", str(packet_dir)])
    result = json.loads(capsys.readouterr().out)

    assert status == 0
    assert result["record_type"] == "artifact_manifest_read_result"
    assert result["packet_id"] == packet_dir.name
    assert result["manifest_path"] == "artifact_manifest.json"
    assert result["artifact_count"] == 8
    assert result["artifact_manifest"]["record_type"] == "artifact_manifest"
    assert "does not prove correctness" in result["authority_note"]


def test_cli_hash_summary_emits_compact_hash_result(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)

    status = main(["hash-summary", str(packet_dir)])
    result = json.loads(capsys.readouterr().out)

    assert status == 0
    assert result["record_type"] == "artifact_hash_summary"
    assert result["packet_id"] == packet_dir.name
    assert result["verification_status"] == "passed_mechanical_checks"
    assert result["hash_algorithm"] == "sha256"
    assert result["artifact_count"] == 8
    assert result["hashed_artifact_count"] == 7
    assert result["unhashed_artifact_count"] == 1
    assert result["missing_artifact_count"] == 0
    assert result["hash_mismatch_count"] == 0
    assert "artifact_manifest" not in result


def test_cli_hash_summary_returns_nonzero_for_hash_mismatch(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)
    (packet_dir / "context_pack.md").write_text("tampered context\n", encoding="utf-8")

    status = main(["hash-summary", str(packet_dir)])
    result = json.loads(capsys.readouterr().out)

    assert status != 0
    assert result["verification_status"] == "failed_mechanical_checks"
    assert result["hash_mismatch_count"] == 1
    assert any(
        artifact["path"] == "context_pack.md" and artifact["hash_status"] == "hash_mismatch"
        for artifact in result["artifacts"]
    )


def test_cli_schema_index_emits_static_contract_discovery(capsys):
    status = main(["schema-index"])
    result = json.loads(capsys.readouterr().out)

    assert status == 0
    assert result["schema_version"] == "0.1"
    assert result["record_type"] == "schema_index"
    assert result["schema_scope"] == "static_json_artifact_contracts_only"
    assert result["schema_count"] == 7
    assert result["artifact_count"] == 7
    assert result["missing_schema_files"] == []
    assert {entry["artifact"] for entry in result["schemas"]} == {
        "query_job.json",
        "retrieval_record.json",
        "source_citations.json",
        "notebook_run_record.json",
        "environment_report.json",
        "artifact_manifest.json",
        "replay_manifest.json",
    }
    assert "scientific validation" in result["authority_note"]


def test_cli_schema_contract_emits_single_static_contract(capsys):
    status = main(["schema-contract", "query_job.json"])
    result = json.loads(capsys.readouterr().out)

    assert status == 0
    assert result["schema_version"] == "0.1"
    assert result["record_type"] == "schema_contract"
    assert result["schema_scope"] == "static_json_artifact_contracts_only"
    assert result["artifact"] == "query_job.json"
    assert result["schema_file"] == "query_job.schema.json"
    assert result["expected_record_type"] == "query_job"
    assert "request_text" in result["required_fields"]
    assert result["schema"]["type"] == "object"


def test_cli_schema_contract_returns_nonzero_for_unknown_artifact(capsys):
    status = main(["schema-contract", "not_a_packet_record.json"])
    err = capsys.readouterr().err.lower()

    assert status != 0
    assert "unknown schema artifact" in err


def test_cli_export_zip_emits_static_export_result(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)
    output_zip = tmp_path / "exports" / "packet.zip"
    output_zip.parent.mkdir()

    status = main(["export-zip", str(packet_dir), "--output-zip", str(output_zip)])
    result = json.loads(capsys.readouterr().out)

    assert status == 0
    assert result["schema_version"] == "0.1"
    assert result["record_type"] == "packet_zip_export_result"
    assert result["packet_id"] == packet_dir.name
    assert result["output_zip"] == str(output_zip)
    assert result["export_status"] == "exported"
    assert result["export_scope"] == "static_packet_archive_only"
    assert result["archive_format"] == "zip"
    assert result["zip_entry_count"] == 8
    assert result["verification_status"] == "passed_mechanical_checks"
    assert output_zip.exists()


def test_cli_export_zip_returns_nonzero_when_output_exists_without_overwrite(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)
    output_zip = tmp_path / "packet.zip"

    first_status = main(["export-zip", str(packet_dir), "--output-zip", str(output_zip)])
    capsys.readouterr()
    second_status = main(["export-zip", str(packet_dir), "--output-zip", str(output_zip)])
    err = capsys.readouterr().err.lower()

    assert first_status == 0
    assert second_status != 0
    assert "already exists" in err


def test_cli_export_zip_returns_failed_status_for_tampered_packet(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)
    output_zip = tmp_path / "packet.zip"
    (packet_dir / "context_pack.md").write_text("tampered context\n", encoding="utf-8")

    status = main(["export-zip", str(packet_dir), "--output-zip", str(output_zip)])
    result = json.loads(capsys.readouterr().out)

    assert status != 0
    assert result["record_type"] == "packet_zip_export_result"
    assert result["verification_status"] == "failed_mechanical_checks"
    assert output_zip.exists()


def test_cli_import_zip_preview_emits_static_preview_result(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)
    output_zip = tmp_path / "packet.zip"

    export_status = main(["export-zip", str(packet_dir), "--output-zip", str(output_zip)])
    capsys.readouterr()
    assert export_status == 0

    status = main(["import-zip-preview", str(output_zip)])
    result = json.loads(capsys.readouterr().out)

    assert status == 0
    assert result["schema_version"] == "0.1"
    assert result["record_type"] == "packet_zip_import_preview_result"
    assert result["packet_id"] == packet_dir.name
    assert result["zip_path"] == str(output_zip)
    assert result["preview_status"] == "previewed"
    assert result["import_status"] == "not_imported_preview_only"
    assert result["verification_status"] == "passed_mechanical_checks"
    assert result["extraction_performed"] is False
    assert result["missing_required_artifact_count"] == 0


def test_cli_import_zip_preview_returns_nonzero_for_incomplete_packet_zip(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)
    incomplete_zip = tmp_path / "incomplete.zip"

    from zipfile import ZipFile

    with ZipFile(incomplete_zip, "w") as archive:
        for path in sorted(packet_dir.iterdir()):
            if path.name == "retrieval_record.json":
                continue
            archive.write(path, arcname=f"{packet_dir.name}/{path.name}")

    status = main(["import-zip-preview", str(incomplete_zip)])
    result = json.loads(capsys.readouterr().out)

    assert status != 0
    assert result["record_type"] == "packet_zip_import_preview_result"
    assert result["preview_status"] == "preview_failed"
    assert result["verification_status"] == "failed_mechanical_checks"
    assert result["missing_required_artifacts"] == ["retrieval_record.json"]


def test_cli_import_zip_preview_returns_nonzero_for_unsafe_zip(tmp_path, capsys):
    from zipfile import ZipFile

    unsafe_zip = tmp_path / "unsafe.zip"
    with ZipFile(unsafe_zip, "w") as archive:
        archive.writestr("../evil.txt", "bad")

    status = main(["import-zip-preview", str(unsafe_zip)])
    err = capsys.readouterr().err.lower()

    assert status != 0
    assert "unsafe zip entry" in err



def test_cli_import_zip_extract_emits_static_import_result(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)
    output_zip = tmp_path / "packet.zip"
    output_root = tmp_path / "imports"
    output_root.mkdir()

    export_status = main(["export-zip", str(packet_dir), "--output-zip", str(output_zip)])
    capsys.readouterr()
    assert export_status == 0

    status = main(["import-zip-extract", str(output_zip), "--output-root", str(output_root)])
    result = json.loads(capsys.readouterr().out)

    assert status == 0
    assert result["schema_version"] == "0.1"
    assert result["record_type"] == "packet_zip_import_result"
    assert result["packet_id"] == packet_dir.name
    assert result["import_status"] == "imported"
    assert result["extraction_status"] == "extracted"
    assert result["import_scope"] == "static_zip_safe_extract_only"
    assert result["verification_status"] == "passed_mechanical_checks"
    assert result["extraction_performed"] is True
    assert Path(result["extracted_packet_dir"]).exists()


def test_cli_import_zip_extract_refuses_existing_destination_without_overwrite(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)
    output_zip = tmp_path / "packet.zip"
    output_root = tmp_path / "imports"
    output_root.mkdir()
    (output_root / packet_dir.name).mkdir()

    export_status = main(["export-zip", str(packet_dir), "--output-zip", str(output_zip)])
    capsys.readouterr()
    assert export_status == 0

    status = main(["import-zip-extract", str(output_zip), "--output-root", str(output_root)])
    err = capsys.readouterr().err.lower()

    assert status != 0
    assert "already exists" in err


def test_cli_import_zip_extract_supports_pretty_json(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)
    output_zip = tmp_path / "packet.zip"
    output_root = tmp_path / "imports"
    output_root.mkdir()

    export_status = main(["export-zip", str(packet_dir), "--output-zip", str(output_zip)])
    capsys.readouterr()
    assert export_status == 0

    status = main(["import-zip-extract", str(output_zip), "--output-root", str(output_root), "--pretty"])
    raw = capsys.readouterr().out
    result = json.loads(raw)

    assert status == 0
    assert "\n  " in raw
    assert result["record_type"] == "packet_zip_import_result"
