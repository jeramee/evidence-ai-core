import json
import socket
import subprocess
from pathlib import Path

import pytest

from evidence_ai_core import PacketInputError, create_static_packet, summarize_packet
from evidence_ai_core.constants import AUTHORITY_FLAGS, REQUIRED_ARTIFACTS


def make_packet(tmp_path: Path) -> Path:
    source = tmp_path / "source.md"
    source.write_text("# Source\nEvidence text.", encoding="utf-8")
    return create_static_packet("summary request", [str(source)], tmp_path / "packets")


def test_summarize_packet_returns_compact_stable_contract(tmp_path):
    packet = make_packet(tmp_path)

    summary = summarize_packet(packet)

    assert summary["schema_version"] == "0.1"
    assert summary["record_type"] == "packet_summary"
    assert summary["packet_id"] == packet.name
    assert summary["packet_dir"] == str(packet)
    assert summary["artifact_count"] == len(REQUIRED_ARTIFACTS)
    assert summary["required_artifact_count"] == len(REQUIRED_ARTIFACTS)
    assert summary["missing_artifact_count"] == 0
    assert summary["json_record_count"] == 7
    assert summary["text_artifact_count"] == 1
    assert summary["verification_status"] == "passed_mechanical_checks"
    assert summary["verification_scope"] == "mechanical_packet_shape_only"
    assert summary["check_count"] == 6
    assert summary["error_count"] == 0
    assert summary["warning_count"] >= 0
    assert summary["check_status_counts"]["passed"] == 6
    assert summary["authority_flags"] == AUTHORITY_FLAGS
    assert "Evidence is not proof" in summary["authority_note"]
    assert "does_not_prove_scientific_correctness" in summary["limitations"]
    assert {artifact["path"] for artifact in summary["artifacts"]} == set(REQUIRED_ARTIFACTS)
    assert all(artifact["required"] is True for artifact in summary["artifacts"])
    assert all(artifact["exists"] is True for artifact in summary["artifacts"])
    assert "json_records" not in summary
    assert "text_artifacts" not in summary
    assert "verification_result" not in summary


def test_summarize_packet_reports_missing_artifact_without_full_records(tmp_path):
    packet = make_packet(tmp_path)
    (packet / "retrieval_record.json").unlink()

    summary = summarize_packet(packet)

    assert summary["verification_status"] == "failed_mechanical_checks"
    assert summary["missing_artifact_count"] == 1
    assert summary["error_count"] >= 1
    missing_artifacts = [artifact for artifact in summary["artifacts"] if not artifact["exists"]]
    assert missing_artifacts == [
        {
            "path": "retrieval_record.json",
            "artifact_type": "json",
            "required": True,
            "exists": False,
        }
    ]
    assert "json_records" not in summary
    assert "text_artifacts" not in summary


def test_summarize_packet_rejects_missing_packet_directory(tmp_path):
    with pytest.raises(PacketInputError, match="packet directory does not exist"):
        summarize_packet(tmp_path / "missing")


def test_summarize_packet_is_read_only(tmp_path):
    packet = make_packet(tmp_path)
    before = sorted((path.name, path.stat().st_mtime_ns) for path in packet.iterdir())

    summary = summarize_packet(packet)

    after = sorted((path.name, path.stat().st_mtime_ns) for path in packet.iterdir())
    assert summary["verification_status"] == "passed_mechanical_checks"
    assert after == before


def test_summarize_packet_does_not_require_network_or_subprocess(tmp_path, monkeypatch):
    def fail_network(*args, **kwargs):
        raise AssertionError("network calls are forbidden for evidence-ai-core packet summary")

    def fail_subprocess(*args, **kwargs):
        raise AssertionError("subprocess calls are forbidden for evidence-ai-core packet summary")

    monkeypatch.setattr(socket, "socket", fail_network)
    monkeypatch.setattr(subprocess, "run", fail_subprocess)
    monkeypatch.setattr(subprocess, "Popen", fail_subprocess)

    packet = make_packet(tmp_path)
    summary = summarize_packet(packet)

    assert summary["verification_status"] == "passed_mechanical_checks"
    assert summary["record_type"] == "packet_summary"
