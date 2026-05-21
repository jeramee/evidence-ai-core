import json
import socket
import subprocess
from pathlib import Path

import pytest

from evidence_ai_core import create_static_packet, read_artifact_manifest, summarize_artifact_hashes
from evidence_ai_core.errors import PacketReadError


def make_packet(tmp_path: Path) -> Path:
    source = tmp_path / "source.md"
    source.write_text("# Source\nEvidence text.", encoding="utf-8")
    return create_static_packet("manifest request", [str(source)], tmp_path / "packets")


def test_read_artifact_manifest_returns_stable_read_contract(tmp_path):
    packet = make_packet(tmp_path)

    result = read_artifact_manifest(packet)

    assert result["schema_version"] == "0.1"
    assert result["record_type"] == "artifact_manifest_read_result"
    assert result["packet_id"] == packet.name
    assert result["packet_dir"] == str(packet)
    assert result["manifest_path"] == "artifact_manifest.json"
    assert result["artifact_count"] == 8
    assert result["artifact_manifest"]["record_type"] == "artifact_manifest"
    assert result["artifact_manifest"]["packet_id"] == packet.name
    assert result["authority_flags"]["correctness_proven"] is False
    assert "does not prove correctness" in result["authority_note"]


def test_summarize_artifact_hashes_returns_compact_hash_contract(tmp_path):
    packet = make_packet(tmp_path)

    result = summarize_artifact_hashes(packet)

    assert result["schema_version"] == "0.1"
    assert result["record_type"] == "artifact_hash_summary"
    assert result["packet_id"] == packet.name
    assert result["verification_status"] == "passed_mechanical_checks"
    assert result["verification_scope"] == "artifact_manifest_hash_summary_only"
    assert result["hash_algorithm"] == "sha256"
    assert result["artifact_count"] == 8
    assert result["hashed_artifact_count"] == 7
    assert result["unhashed_artifact_count"] == 1
    assert result["missing_artifact_count"] == 0
    assert result["hash_mismatch_count"] == 0
    assert result["malformed_entry_count"] == 0
    assert "artifact_manifest" not in result
    assert all("expected_hash" in artifact for artifact in result["artifacts"])
    assert any(
        artifact["path"] == "artifact_manifest.json" and artifact["hash_status"] == "hash_not_recorded"
        for artifact in result["artifacts"]
    )


def test_summarize_artifact_hashes_reports_hash_mismatch(tmp_path):
    packet = make_packet(tmp_path)
    (packet / "context_pack.md").write_text("tampered context\n", encoding="utf-8")

    result = summarize_artifact_hashes(packet)

    assert result["verification_status"] == "failed_mechanical_checks"
    assert result["hash_mismatch_count"] == 1
    assert any(
        artifact["path"] == "context_pack.md" and artifact["hash_status"] == "hash_mismatch"
        for artifact in result["artifacts"]
    )


def test_read_artifact_manifest_fails_for_invalid_manifest_json(tmp_path):
    packet = make_packet(tmp_path)
    (packet / "artifact_manifest.json").write_text("{invalid json", encoding="utf-8")

    with pytest.raises(PacketReadError, match="artifact_manifest.json: invalid JSON"):
        read_artifact_manifest(packet)


def test_manifest_reader_and_hash_summary_do_not_require_external_actions(tmp_path, monkeypatch):
    def fail_network(*args, **kwargs):
        raise AssertionError("network calls are forbidden for manifest APIs")

    def fail_subprocess(*args, **kwargs):
        raise AssertionError("subprocess calls are forbidden for manifest APIs")

    monkeypatch.setattr(socket, "socket", fail_network)
    monkeypatch.setattr(subprocess, "run", fail_subprocess)
    monkeypatch.setattr(subprocess, "Popen", fail_subprocess)

    packet = make_packet(tmp_path)
    manifest = read_artifact_manifest(packet)
    hash_summary = summarize_artifact_hashes(packet)

    assert manifest["record_type"] == "artifact_manifest_read_result"
    assert hash_summary["verification_status"] == "passed_mechanical_checks"
