import json
import socket
import subprocess
from pathlib import Path

import pytest

from evidence_ai_core import list_schema_contracts, load_schema_contract
from evidence_ai_core.errors import PacketInputError, PacketReadError


def test_list_schema_contracts_returns_static_schema_index():
    result = list_schema_contracts()

    assert result["schema_version"] == "0.1"
    assert result["record_type"] == "schema_index"
    assert result["schema_scope"] == "static_json_artifact_contracts_only"
    assert result["schema_count"] == 7
    assert result["artifact_count"] == 7
    assert result["missing_schema_files"] == []
    assert result["authority_note"].startswith("Schema contracts are static shape contracts only.")
    assert "does_not_validate_json_instances_at_runtime" in result["limitations"]

    artifacts = {entry["artifact"] for entry in result["schemas"]}
    assert artifacts == {
        "query_job.json",
        "retrieval_record.json",
        "source_citations.json",
        "notebook_run_record.json",
        "environment_report.json",
        "artifact_manifest.json",
        "replay_manifest.json",
    }


def test_schema_index_entries_expose_minimum_contract_shape():
    result = list_schema_contracts()
    query_job = next(entry for entry in result["schemas"] if entry["artifact"] == "query_job.json")

    assert query_job["schema_file"] == "query_job.schema.json"
    assert query_job["title"] == "query_job"
    assert query_job["draft"] == "https://json-schema.org/draft/2020-12/schema"
    assert query_job["expected_record_type"] == "query_job"
    assert query_job["required_field_count"] == len(query_job["required_fields"])
    assert "request_text" in query_job["required_fields"]
    assert "authority_flags" in query_job["property_names"]
    assert query_job["has_authority_flags_contract"] is True


def test_load_schema_contract_accepts_artifact_schema_filename_and_record_stem():
    by_artifact = load_schema_contract("query_job.json")
    by_schema = load_schema_contract("query_job.schema.json")
    by_stem = load_schema_contract("query_job")

    assert by_artifact["record_type"] == "schema_contract"
    assert by_artifact["schema_scope"] == "static_json_artifact_contracts_only"
    assert by_artifact["artifact"] == "query_job.json"
    assert by_artifact["schema_file"] == "query_job.schema.json"
    assert by_artifact["expected_record_type"] == "query_job"
    assert by_artifact["required_fields"] == by_schema["required_fields"] == by_stem["required_fields"]
    assert by_artifact["schema"]["properties"]["record_type"]["const"] == "query_job"


def test_schema_contract_rejects_unknown_artifact():
    with pytest.raises(PacketInputError, match="unknown schema artifact"):
        load_schema_contract("unknown_record.json")


def test_schema_contract_fails_clearly_for_invalid_schema_json(tmp_path):
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    (schema_dir / "query_job.schema.json").write_text("{not valid json", encoding="utf-8")

    with pytest.raises(PacketReadError, match="query_job.schema.json: invalid JSON"):
        load_schema_contract("query_job.json", schema_dir=schema_dir)


def test_schema_index_does_not_require_network_or_subprocess(monkeypatch):
    def fail_network(*args, **kwargs):
        raise AssertionError("network calls are forbidden for schema discovery")

    def fail_subprocess(*args, **kwargs):
        raise AssertionError("subprocess calls are forbidden for schema discovery")

    monkeypatch.setattr(socket, "socket", fail_network)
    monkeypatch.setattr(subprocess, "run", fail_subprocess)
    monkeypatch.setattr(subprocess, "Popen", fail_subprocess)

    index = list_schema_contracts()
    contract = load_schema_contract("query_job.json")

    assert index["record_type"] == "schema_index"
    assert contract["record_type"] == "schema_contract"
