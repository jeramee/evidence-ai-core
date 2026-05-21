import json
import socket
import subprocess
from pathlib import Path

from evidence_ai_core import (
    create_static_packet,
    export_packet_zip,
    export_packet_inventory_jsonl,
    extract_packet_zip,
    preview_packet_zip,
    inventory_packet_bundle,
    list_schema_contracts,
    load_packet,
    load_schema_contract,
    read_artifact_manifest,
    summarize_artifact_hashes,
    summarize_packet,
    verify_packet,
)
from evidence_ai_core.cli import main
from evidence_ai_core.inspect import inspect_packet


FORBIDDEN_IMPORTS = (
    "txtai",
    "paperetl",
    "paperai",
    "papermill",
    "jupyter",
    "quarto",
    "gitpython",
    "jsonschema",
)


def make_source(tmp_path: Path) -> Path:
    source = tmp_path / "source.md"
    source.write_text("# Source\nEvidence text.", encoding="utf-8")
    return source


def test_api_static_packet_and_verify_do_not_require_network_or_subprocess(
    tmp_path,
    monkeypatch,
):
    def fail_network(*args, **kwargs):
        raise AssertionError("network calls are forbidden for evidence-ai-core API")

    def fail_subprocess(*args, **kwargs):
        raise AssertionError("subprocess calls are forbidden for evidence-ai-core API")

    monkeypatch.setattr(socket, "socket", fail_network)
    monkeypatch.setattr(subprocess, "run", fail_subprocess)
    monkeypatch.setattr(subprocess, "Popen", fail_subprocess)

    source = make_source(tmp_path)
    packet = create_static_packet("guardrail request", [str(source)], tmp_path / "packets")
    verification = verify_packet(packet)
    inspection = inspect_packet(packet)
    loaded = load_packet(packet)
    manifest = read_artifact_manifest(packet)
    hash_summary = summarize_artifact_hashes(packet)
    summary = summarize_packet(packet)
    schema_index = list_schema_contracts()
    schema_contract = load_schema_contract("query_job.json")
    export_result = export_packet_zip(packet, tmp_path / "packet.zip")
    (tmp_path / "imports").mkdir()
    import_preview = preview_packet_zip(tmp_path / "packet.zip")
    import_extract = extract_packet_zip(tmp_path / "packet.zip", tmp_path / "imports")
    inventory = inventory_packet_bundle(tmp_path, recursive=True)
    inventory_jsonl = export_packet_inventory_jsonl(tmp_path, tmp_path / "inventory.jsonl", recursive=True)

    assert verification["verification_status"] == "passed_mechanical_checks"
    assert inspection["verification_status"] == "passed_mechanical_checks"
    assert loaded["verification_status"] == "passed_mechanical_checks"
    assert manifest["record_type"] == "artifact_manifest_read_result"
    assert hash_summary["verification_status"] == "passed_mechanical_checks"
    assert summary["verification_status"] == "passed_mechanical_checks"
    assert schema_index["record_type"] == "schema_index"
    assert schema_contract["record_type"] == "schema_contract"
    assert export_result["record_type"] == "packet_zip_export_result"
    assert import_preview["record_type"] == "packet_zip_import_preview_result"
    assert import_extract["record_type"] == "packet_zip_import_result"
    assert inventory["record_type"] == "packet_bundle_inventory"
    assert inventory_jsonl["record_type"] == "packet_bundle_inventory_jsonl_export"


def test_cli_create_verify_inspect_do_not_require_network_or_subprocess(
    tmp_path,
    monkeypatch,
    capsys,
):
    def fail_network(*args, **kwargs):
        raise AssertionError("network calls are forbidden for evidence-ai-core CLI")

    def fail_subprocess(*args, **kwargs):
        raise AssertionError("subprocess calls are forbidden for evidence-ai-core CLI")

    monkeypatch.setattr(socket, "socket", fail_network)
    monkeypatch.setattr(subprocess, "run", fail_subprocess)
    monkeypatch.setattr(subprocess, "Popen", fail_subprocess)

    source = make_source(tmp_path)
    output_root = tmp_path / "packets"

    create_status = main(
        [
            "create-static",
            "--request-text",
            "guardrail cli request",
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

    schema_index_status = main(["schema-index"])
    schema_index_result = json.loads(capsys.readouterr().out)

    schema_contract_status = main(["schema-contract", "query_job.json"])
    schema_contract_result = json.loads(capsys.readouterr().out)

    export_zip = tmp_path / "packet.zip"
    export_status = main(["export-zip", str(packet_dir), "--output-zip", str(export_zip)])
    export_result = json.loads(capsys.readouterr().out)

    import_preview_status = main(["import-zip-preview", str(export_zip)])
    import_preview_result = json.loads(capsys.readouterr().out)

    import_root = tmp_path / "cli-imports"
    import_root.mkdir()
    import_extract_status = main(["import-zip-extract", str(export_zip), "--output-root", str(import_root)])
    import_extract_result = json.loads(capsys.readouterr().out)

    inventory_status = main(["bundle-inventory", str(tmp_path), "--recursive"])
    inventory_result = json.loads(capsys.readouterr().out)

    inventory_jsonl = tmp_path / "cli-inventory.jsonl"
    inventory_jsonl_status = main(["bundle-inventory-jsonl", str(tmp_path), "--output-jsonl", str(inventory_jsonl), "--recursive"])
    inventory_jsonl_result = json.loads(capsys.readouterr().out)

    assert create_status == 0
    assert verify_status == 0
    assert inspect_status == 0
    assert summary_status == 0
    assert manifest_status == 0
    assert hash_summary_status == 0
    assert schema_index_status == 0
    assert schema_contract_status == 0
    assert export_status == 0
    assert import_preview_status == 0
    assert import_extract_status == 0
    assert inventory_status == 0
    assert inventory_jsonl_status == 0
    assert verify_result["verification_status"] == "passed_mechanical_checks"
    assert inspect_result["verification_status"] == "passed_mechanical_checks"
    assert summary_result["verification_status"] == "passed_mechanical_checks"
    assert manifest_result["record_type"] == "artifact_manifest_read_result"
    assert hash_summary_result["verification_status"] == "passed_mechanical_checks"
    assert schema_index_result["record_type"] == "schema_index"
    assert schema_contract_result["record_type"] == "schema_contract"
    assert export_result["record_type"] == "packet_zip_export_result"
    assert import_preview_result["record_type"] == "packet_zip_import_preview_result"
    assert import_extract_result["record_type"] == "packet_zip_import_result"
    assert inventory_result["record_type"] == "packet_bundle_inventory"
    assert inventory_jsonl_result["record_type"] == "packet_bundle_inventory_jsonl_export"


def test_package_does_not_import_runtime_adapter_dependencies():
    package_root = Path("src/evidence_ai_core")
    source_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in package_root.glob("*.py")
        if path.name != "__pycache__"
    ).lower()

    for forbidden in FORBIDDEN_IMPORTS:
        assert f"import {forbidden}" not in source_text
        assert f"from {forbidden}" not in source_text
