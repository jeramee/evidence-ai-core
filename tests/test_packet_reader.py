import json
import socket
import subprocess
from pathlib import Path

import pytest

from evidence_ai_core import PacketInputError, PacketReadError, create_static_packet, load_packet
from evidence_ai_core.constants import AUTHORITY_FLAGS, REQUIRED_ARTIFACTS


def make_packet(tmp_path: Path) -> Path:
    source = tmp_path / "source.md"
    source.write_text("# Source\nEvidence text.", encoding="utf-8")
    return create_static_packet("reader request", [str(source)], tmp_path / "packets")


def test_load_packet_returns_static_read_contract(tmp_path):
    packet = make_packet(tmp_path)

    loaded = load_packet(packet)

    assert loaded["schema_version"] == "0.1"
    assert loaded["record_type"] == "packet_read_result"
    assert loaded["packet_id"] == packet.name
    assert loaded["packet_dir"] == str(packet)
    assert loaded["artifact_names"] == REQUIRED_ARTIFACTS
    assert set(loaded["json_records"]) == {name for name in REQUIRED_ARTIFACTS if name.endswith(".json")}
    assert "context_pack.md" in loaded["text_artifacts"]
    assert loaded["verification_status"] == "passed_mechanical_checks"
    assert loaded["verification_result"]["record_type"] == "verification_result"
    assert loaded["authority_flags"] == AUTHORITY_FLAGS
    assert "read-only" in loaded["authority_note"]
    assert "does not prove correctness" in loaded["authority_note"]


def test_load_packet_is_read_only(tmp_path):
    packet = make_packet(tmp_path)
    before = sorted((path.name, path.stat().st_mtime_ns) for path in packet.iterdir())

    loaded = load_packet(packet)

    after = sorted((path.name, path.stat().st_mtime_ns) for path in packet.iterdir())
    assert loaded["verification_status"] == "passed_mechanical_checks"
    assert after == before


def test_load_packet_rejects_missing_packet_directory(tmp_path):
    missing = tmp_path / "missing-packet"

    with pytest.raises(PacketInputError, match="packet directory does not exist"):
        load_packet(missing)


def test_load_packet_rejects_file_path_instead_of_directory(tmp_path):
    packet_file = tmp_path / "not-a-packet.txt"
    packet_file.write_text("not a directory", encoding="utf-8")

    with pytest.raises(PacketInputError, match="packet path is not a directory"):
        load_packet(packet_file)


def test_load_packet_fails_clearly_on_invalid_json(tmp_path):
    packet = make_packet(tmp_path)
    (packet / "query_job.json").write_text("{not valid json", encoding="utf-8")

    with pytest.raises(PacketReadError, match="query_job.json: invalid JSON"):
        load_packet(packet)


def test_load_packet_does_not_require_network_or_subprocess(tmp_path, monkeypatch):
    def fail_network(*args, **kwargs):
        raise AssertionError("network calls are forbidden for evidence-ai-core packet reader")

    def fail_subprocess(*args, **kwargs):
        raise AssertionError("subprocess calls are forbidden for evidence-ai-core packet reader")

    monkeypatch.setattr(socket, "socket", fail_network)
    monkeypatch.setattr(subprocess, "run", fail_subprocess)
    monkeypatch.setattr(subprocess, "Popen", fail_subprocess)

    packet = make_packet(tmp_path)
    loaded = load_packet(packet)

    assert loaded["verification_status"] == "passed_mechanical_checks"
    assert loaded["json_records"]["query_job.json"]["request_text"] == "reader request"
