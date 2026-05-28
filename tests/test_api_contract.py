import socket
import subprocess
from pathlib import Path

import pytest

import evidence_ai_core
from evidence_ai_core import (
    EvidenceCoreError,
    PacketAlreadyExistsError,
    PacketInputError,
    PacketReadError,
    PacketVerificationError,
    PacketExportError,
    PacketImportError,
    create_static_packet,
    export_packet_zip,
    export_packet_inventory_jsonl,
    extract_packet_zip,
    preview_packet_zip,
    inspect_packet,
    inventory_packet_bundle,
    list_schema_contracts,
    load_packet,
    load_schema_contract,
    read_artifact_manifest,
    summarize_artifact_hashes,
    summarize_packet,
    verify_packet,
)


def make_source(tmp_path: Path) -> Path:
    source = tmp_path / "source.md"
    source.write_text("# Source\nEvidence text.", encoding="utf-8")
    return source


def test_public_exports_include_static_packet_api_and_error_contract():
    expected_exports = {
        "EvidenceCoreError",
        "PacketAlreadyExistsError",
        "PacketInputError",
        "PacketReadError",
        "PacketVerificationError",
        "create_static_packet",
        "export_packet_zip",
        "export_packet_inventory_jsonl",
        "extract_packet_zip",
        "preview_packet_zip",
        "PacketExportError",
        "PacketImportError",
        "inspect_packet",
        "inventory_packet_bundle",
        "list_schema_contracts",
        "load_schema_contract",
        "read_artifact_manifest",
        "verify_packet",
    }

    assert expected_exports.issubset(set(evidence_ai_core.__all__))
    assert callable(create_static_packet)
    assert callable(export_packet_zip)
    assert callable(export_packet_inventory_jsonl)
    assert callable(extract_packet_zip)
    assert callable(preview_packet_zip)
    assert callable(inspect_packet)
    assert callable(inventory_packet_bundle)
    assert callable(list_schema_contracts)
    assert callable(load_packet)
    assert callable(load_schema_contract)
    assert callable(read_artifact_manifest)
    assert callable(summarize_artifact_hashes)
    assert callable(summarize_packet)
    assert callable(verify_packet)
    assert issubclass(PacketInputError, EvidenceCoreError)
    assert issubclass(PacketAlreadyExistsError, PacketInputError)
    assert issubclass(PacketReadError, EvidenceCoreError)
    assert issubclass(PacketExportError, EvidenceCoreError)
    assert issubclass(PacketImportError, EvidenceCoreError)
    assert issubclass(PacketVerificationError, EvidenceCoreError)


def test_create_static_packet_rejects_empty_request_text(tmp_path):
    source = make_source(tmp_path)

    with pytest.raises(PacketInputError, match="request_text must not be empty"):
        create_static_packet("", [str(source)], tmp_path / "packets")


def test_create_static_packet_rejects_missing_source_paths(tmp_path):
    with pytest.raises(PacketInputError, match="at least one source path is required"):
        create_static_packet("request", [], tmp_path / "packets")


def test_create_static_packet_rejects_missing_source_file(tmp_path):
    missing_source = tmp_path / "missing.md"

    with pytest.raises(PacketInputError, match="source file does not exist"):
        create_static_packet("request", [str(missing_source)], tmp_path / "packets")


def test_create_static_packet_rejects_source_directory(tmp_path):
    source_dir = tmp_path / "source-dir"
    source_dir.mkdir()

    with pytest.raises(PacketInputError, match="source path is not a file"):
        create_static_packet("request", [str(source_dir)], tmp_path / "packets")


def test_create_static_packet_refuses_to_overwrite_existing_packet_dir(tmp_path, monkeypatch):
    source = make_source(tmp_path)

    monkeypatch.setattr("evidence_ai_core.packet.make_packet_id", lambda request_text, created_at: "fixed_packet_id")

    first_packet = create_static_packet("request", [str(source)], tmp_path / "packets")
    assert first_packet.exists()

    with pytest.raises(PacketAlreadyExistsError, match="would not be overwritten"):
        create_static_packet("request", [str(source)], tmp_path / "packets")


def test_public_api_contract_does_not_require_network_or_subprocess(tmp_path, monkeypatch):
    def fail_network(*args, **kwargs):
        raise AssertionError("network calls are forbidden for evidence-ai-core public API")

    def fail_subprocess(*args, **kwargs):
        raise AssertionError("subprocess calls are forbidden for evidence-ai-core public API")

    monkeypatch.setattr(socket, "socket", fail_network)
    monkeypatch.setattr(subprocess, "run", fail_subprocess)
    monkeypatch.setattr(subprocess, "Popen", fail_subprocess)

    source = make_source(tmp_path)
    packet = create_static_packet("request", [str(source)], tmp_path / "packets")
    verification = verify_packet(packet)
    inspection = inspect_packet(packet)
    loaded = load_packet(packet)
    manifest = read_artifact_manifest(packet)
    hash_summary = summarize_artifact_hashes(packet)
    summary = summarize_packet(packet)
    schema_index = list_schema_contracts()
    schema_contract = load_schema_contract("query_job.json")
    inventory = inventory_packet_bundle(tmp_path / "packets")
    inventory_jsonl = export_packet_inventory_jsonl(tmp_path / "packets", tmp_path / "inventory.jsonl")

    assert verification["verification_status"] == "passed_mechanical_checks"
    assert inspection["verification_status"] == "passed_mechanical_checks"
    assert loaded["verification_status"] == "passed_mechanical_checks"
    assert manifest["record_type"] == "artifact_manifest_read_result"
    assert hash_summary["verification_status"] == "passed_mechanical_checks"
    assert summary["verification_status"] == "passed_mechanical_checks"
    assert schema_index["record_type"] == "schema_index"
    assert schema_contract["record_type"] == "schema_contract"
    assert inventory["record_type"] == "packet_bundle_inventory"
    assert inventory_jsonl["record_type"] == "packet_bundle_inventory_jsonl_export"

def test_external_tool_evidence_public_api_contract():
    assert "verify_external_tool_evidence_envelope" in evidence_ai_core.__all__
    assert "EXTERNAL_TOOL_EVIDENCE_RECORD_TYPE" in evidence_ai_core.__all__
    assert "EXTERNAL_TOOL_EVIDENCE_SCHEMA_VERSION" in evidence_ai_core.__all__

    assert callable(evidence_ai_core.verify_external_tool_evidence_envelope)
    assert evidence_ai_core.EXTERNAL_TOOL_EVIDENCE_RECORD_TYPE == "external_tool_evidence_envelope"
    assert evidence_ai_core.EXTERNAL_TOOL_EVIDENCE_SCHEMA_VERSION == "0.1"

    envelope = {
        "record_type": evidence_ai_core.EXTERNAL_TOOL_EVIDENCE_RECORD_TYPE,
        "schema_version": evidence_ai_core.EXTERNAL_TOOL_EVIDENCE_SCHEMA_VERSION,
        "trace_id": "trace_public_api_001",
        "tool_family": "txtai",
        "tool_role": "retrieval_index",
        "artifacts": [
            {
                "artifact_id": "artifact_txtai_config",
                "artifact_role": "config",
                "path": "configs/txtai.yml",
                "sha256": "a" * 64,
                "required_for_verification": True,
            }
        ],
        "mechanical_verification_status": evidence_ai_core.MECHANICAL_STATUS_NOT_CHECKED,
        "authority_limits": [
            "mechanical_integrity_only",
            "no_truth_validation",
            "no_model_authority",
            "no_claim_promotion",
            "no_rag_answer_validation",
            "no_external_tool_execution",
        ],
    }

    result = evidence_ai_core.verify_external_tool_evidence_envelope(envelope)

    assert result["record_type"] == "external_tool_evidence_verification_result"
    assert result["trace_id"] == "trace_public_api_001"
    assert result["mechanical_verification_status"] == evidence_ai_core.MECHANICAL_STATUS_PASSED
    assert result["error_count"] == 0

