from copy import deepcopy
import hashlib

from evidence_ai_core.external_tool_evidence import (
    MECHANICAL_STATUS_FAILED,
    MECHANICAL_STATUS_PASSED,
    MECHANICAL_STATUS_PASSED_WITH_WARNINGS,
    MECHANICAL_STATUS_UNSUPPORTED,
    verify_external_tool_evidence_envelope,
)


def minimal_envelope() -> dict:
    return {
        "record_type": "external_tool_evidence_envelope",
        "schema_version": "0.1",
        "trace_id": "trace_txtai_001",
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
        "mechanical_verification_status": "not_checked",
        "authority_limits": [
            "mechanical_integrity_only",
            "no_truth_validation",
            "no_model_authority",
            "no_claim_promotion",
            "no_rag_answer_validation",
            "no_external_tool_execution",
        ],
    }


def issue_codes(result: dict) -> set[str]:
    return {issue["code"] for issue in result["issues"]}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_external_tool_evidence_minimal_txtai_envelope_passes():
    result = verify_external_tool_evidence_envelope(minimal_envelope())

    assert result["record_type"] == "external_tool_evidence_verification_result"
    assert result["trace_id"] == "trace_txtai_001"
    assert result["mechanical_verification_status"] == MECHANICAL_STATUS_PASSED
    assert result["error_count"] == 0
    assert result["warning_count"] == 0
    assert "does not execute external tools" in result["authority_note"]


def test_external_tool_evidence_requires_core_envelope_fields():
    envelope = minimal_envelope()
    del envelope["trace_id"]

    result = verify_external_tool_evidence_envelope(envelope)

    assert result["mechanical_verification_status"] == MECHANICAL_STATUS_FAILED
    assert "required_field_missing" in issue_codes(result)
    assert any(issue.get("field") == "trace_id" for issue in result["errors"])


def test_external_tool_evidence_requires_default_authority_limits():
    envelope = minimal_envelope()
    envelope["authority_limits"] = ["mechanical_integrity_only"]

    result = verify_external_tool_evidence_envelope(envelope)

    assert result["mechanical_verification_status"] == MECHANICAL_STATUS_FAILED
    assert "required_authority_limit_missing" in issue_codes(result)


def test_external_tool_evidence_warns_on_unknown_tool_metadata_without_failing():
    envelope = minimal_envelope()
    envelope["tool_family"] = "custom_local_indexer"
    envelope["tool_role"] = "experimental_role"

    result = verify_external_tool_evidence_envelope(envelope)

    assert result["mechanical_verification_status"] == MECHANICAL_STATUS_PASSED_WITH_WARNINGS
    assert result["error_count"] == 0
    assert {"unknown_tool_family", "unknown_tool_role"}.issubset(issue_codes(result))


def test_external_tool_evidence_warns_on_unknown_artifact_role_required_for_verification():
    envelope = minimal_envelope()
    envelope["artifacts"][0]["artifact_role"] = "unknown"

    result = verify_external_tool_evidence_envelope(envelope)

    assert result["mechanical_verification_status"] == MECHANICAL_STATUS_PASSED_WITH_WARNINGS
    assert result["error_count"] == 0
    assert "unknown_artifact_role_required_for_verification" in issue_codes(result)


def test_external_tool_evidence_rejects_unsafe_artifact_paths():
    unsafe_paths = [
        "/path/outside/bundle",
        "../escape.txt",
        "C:\\absolute\\windows\\path",
        "~/home-relative/path",
    ]

    for unsafe_path in unsafe_paths:
        envelope = minimal_envelope()
        envelope["artifacts"][0]["path"] = unsafe_path

        result = verify_external_tool_evidence_envelope(envelope)

        assert result["mechanical_verification_status"] == MECHANICAL_STATUS_FAILED
        assert "unsafe_artifact_path" in issue_codes(result)


def test_external_tool_evidence_accepts_boring_packet_local_paths():
    safe_paths = [
        "artifacts/index/db.sqlite",
        "manifests/tool_evidence.json",
        "reports/preview.md",
        "logs/local_run.txt",
    ]

    for safe_path in safe_paths:
        envelope = minimal_envelope()
        envelope["artifacts"][0]["path"] = safe_path

        result = verify_external_tool_evidence_envelope(envelope)

        assert result["mechanical_verification_status"] == MECHANICAL_STATUS_PASSED


def test_external_tool_evidence_requires_hash_for_required_artifact():
    envelope = minimal_envelope()
    del envelope["artifacts"][0]["sha256"]

    result = verify_external_tool_evidence_envelope(envelope)

    assert result["mechanical_verification_status"] == MECHANICAL_STATUS_FAILED
    assert "required_artifact_hash_missing" in issue_codes(result)


def test_external_tool_evidence_allows_optional_artifact_without_hash_as_info():
    envelope = minimal_envelope()
    envelope["artifacts"][0]["required_for_verification"] = False
    del envelope["artifacts"][0]["sha256"]

    result = verify_external_tool_evidence_envelope(envelope)

    assert result["mechanical_verification_status"] == MECHANICAL_STATUS_PASSED
    assert "optional_artifact_hash_missing" in issue_codes(result)


def test_external_tool_evidence_returns_unsupported_for_future_schema_version():
    envelope = minimal_envelope()
    envelope["schema_version"] = "9.9"

    result = verify_external_tool_evidence_envelope(envelope)

    assert result["mechanical_verification_status"] == MECHANICAL_STATUS_UNSUPPORTED
    assert result["error_count"] == 0
    assert "unsupported_schema_version" in issue_codes(result)


def test_external_tool_evidence_does_not_mutate_input_envelope():
    envelope = minimal_envelope()
    before = deepcopy(envelope)

    verify_external_tool_evidence_envelope(envelope)

    assert envelope == before


def test_external_tool_evidence_checks_required_artifact_file_hash_when_root_supplied(tmp_path):
    artifact_path = tmp_path / "configs" / "txtai.yml"
    artifact_path.parent.mkdir()
    artifact_path.write_text("path: sqlite\n", encoding="utf-8")

    envelope = minimal_envelope()
    envelope["artifacts"][0]["path"] = "configs/txtai.yml"
    envelope["artifacts"][0]["sha256"] = sha256_text("path: sqlite\n")

    result = verify_external_tool_evidence_envelope(envelope, artifact_root=tmp_path)

    assert result["mechanical_verification_status"] == MECHANICAL_STATUS_PASSED
    assert result["error_count"] == 0


def test_external_tool_evidence_reports_missing_required_artifact_when_root_supplied(tmp_path):
    envelope = minimal_envelope()
    envelope["artifacts"][0]["path"] = "configs/missing.yml"
    envelope["artifacts"][0]["sha256"] = "a" * 64

    result = verify_external_tool_evidence_envelope(envelope, artifact_root=tmp_path)

    assert result["mechanical_verification_status"] == MECHANICAL_STATUS_FAILED
    assert "required_artifact_missing" in issue_codes(result)


def test_external_tool_evidence_reports_hash_mismatch_when_root_supplied(tmp_path):
    artifact_path = tmp_path / "configs" / "txtai.yml"
    artifact_path.parent.mkdir()
    artifact_path.write_text("actual: content\n", encoding="utf-8")

    envelope = minimal_envelope()
    envelope["artifacts"][0]["path"] = "configs/txtai.yml"
    envelope["artifacts"][0]["sha256"] = sha256_text("expected: content\n")

    result = verify_external_tool_evidence_envelope(envelope, artifact_root=tmp_path)

    assert result["mechanical_verification_status"] == MECHANICAL_STATUS_FAILED
    assert "required_artifact_hash_mismatch" in issue_codes(result)


def test_external_tool_evidence_reports_invalid_artifact_root(tmp_path):
    missing_root = tmp_path / "missing-root"

    result = verify_external_tool_evidence_envelope(minimal_envelope(), artifact_root=missing_root)

    assert result["mechanical_verification_status"] == MECHANICAL_STATUS_FAILED
    assert "artifact_root_missing" in issue_codes(result)
