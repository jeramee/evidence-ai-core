import json
import socket
import subprocess
from pathlib import Path

from evidence_ai_core import create_static_packet, verify_packet


REQUIRED_ARTIFACTS = [
    "query_job.json",
    "retrieval_record.json",
    "source_citations.json",
    "context_pack.md",
    "notebook_run_record.json",
    "environment_report.json",
    "artifact_manifest.json",
    "replay_manifest.json",
]


def make_packet(tmp_path: Path) -> Path:
    source = tmp_path / "source.md"
    source.write_text("# Source\nEvidence text.", encoding="utf-8")
    return create_static_packet("demo request", [str(source)], tmp_path / "packets")


def check_failed(result: dict, check_id: str) -> bool:
    return any(
        check["check_id"] == check_id and check["status"] == "failed"
        for check in result["checks"]
    )


def test_create_and_verify_static_packet(tmp_path):
    packet = make_packet(tmp_path)

    for name in REQUIRED_ARTIFACTS:
        assert (packet / name).exists()

    result = verify_packet(packet)

    assert result["verification_status"] == "passed_mechanical_checks"
    assert result["packet_id"] is not None


def test_verifier_fails_on_missing_required_artifact(tmp_path):
    packet = make_packet(tmp_path)

    (packet / "retrieval_record.json").unlink()

    result = verify_packet(packet)

    assert result["verification_status"] == "failed_mechanical_checks"
    assert check_failed(result, "required_files_exist")
    assert "retrieval_record.json" in result["errors"]


def test_verifier_fails_on_invalid_json(tmp_path):
    packet = make_packet(tmp_path)

    (packet / "query_job.json").write_text("{not valid json", encoding="utf-8")

    result = verify_packet(packet)

    assert result["verification_status"] == "failed_mechanical_checks"
    assert check_failed(result, "json_files_parse")
    assert any("query_job.json: invalid JSON" in error for error in result["errors"])


def test_verifier_fails_on_missing_required_field(tmp_path):
    packet = make_packet(tmp_path)

    record_path = packet / "retrieval_record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    del record["retrieval_id"]
    record_path.write_text(json.dumps(record), encoding="utf-8")

    result = verify_packet(packet)

    assert result["verification_status"] == "failed_mechanical_checks"
    assert check_failed(result, "required_fields_present")
    assert "retrieval_record.json: missing retrieval_id" in result["errors"]


def test_verifier_fails_on_packet_id_mismatch(tmp_path):
    packet = make_packet(tmp_path)

    record_path = packet / "replay_manifest.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["packet_id"] = "wrong_packet_id"
    record_path.write_text(json.dumps(record), encoding="utf-8")

    result = verify_packet(packet)

    assert result["verification_status"] == "failed_mechanical_checks"
    assert check_failed(result, "packet_id_consistent")


def test_verifier_fails_on_artifact_hash_mismatch(tmp_path):
    packet = make_packet(tmp_path)

    (packet / "context_pack.md").write_text("tampered context\n", encoding="utf-8")

    result = verify_packet(packet)

    assert result["verification_status"] == "failed_mechanical_checks"
    assert check_failed(result, "artifact_hashes_match")
    assert "context_pack.md: hash mismatch" in result["errors"]


def test_verifier_fails_on_authority_escalation(tmp_path):
    packet = make_packet(tmp_path)

    record_path = packet / "notebook_run_record.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    record["authority_flags"]["correctness_proven"] = True
    record_path.write_text(json.dumps(record), encoding="utf-8")

    result = verify_packet(packet)

    assert result["verification_status"] == "failed_mechanical_checks"
    assert check_failed(result, "authority_flags_not_escalated")
    assert any("correctness_proven=True" in error for error in result["errors"])


def test_static_packet_creation_and_verification_need_no_external_actions(
    tmp_path,
    monkeypatch,
):
    def fail_network(*args, **kwargs):
        raise AssertionError("network calls are forbidden for evidence-ai-core static packets")

    def fail_subprocess(*args, **kwargs):
        raise AssertionError("subprocess calls are forbidden for evidence-ai-core static packets")

    monkeypatch.setattr(socket, "socket", fail_network)
    monkeypatch.setattr(subprocess, "run", fail_subprocess)

    packet = make_packet(tmp_path)
    result = verify_packet(packet)

    assert result["verification_status"] == "passed_mechanical_checks"
