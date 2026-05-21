from pathlib import Path

from evidence_ai_core import create_static_packet, verify_packet
from evidence_ai_core.constants import (
    AUTHORITY_FLAGS,
    CHECK_STATUS_FAILED,
    CHECK_STATUS_PASSED,
    REQUIRED_VERIFICATION_CHECK_IDS,
    VERIFICATION_AUTHORITY_NOTE,
    VERIFICATION_LIMITATIONS,
    VERIFICATION_RESULT_RECORD_TYPE,
    VERIFICATION_SCOPE,
    VERIFICATION_STATUS_FAILED,
    VERIFICATION_STATUS_PASSED,
)


def make_packet(tmp_path: Path) -> Path:
    source = tmp_path / "source.md"
    source.write_text("# Source\nEvidence text.", encoding="utf-8")
    return create_static_packet("verification result contract request", [str(source)], tmp_path / "packets")


def test_verification_result_has_stable_success_contract(tmp_path):
    packet = make_packet(tmp_path)

    result = verify_packet(packet)

    assert result["schema_version"] == "0.1"
    assert result["record_type"] == VERIFICATION_RESULT_RECORD_TYPE
    assert result["packet_id"] == packet.name
    assert result["packet_dir"] == str(packet)
    assert result["verification_status"] == VERIFICATION_STATUS_PASSED
    assert result["verification_scope"] == VERIFICATION_SCOPE
    assert result["authority_flags"] == AUTHORITY_FLAGS
    assert result["authority_note"] == VERIFICATION_AUTHORITY_NOTE
    assert result["limitations"] == VERIFICATION_LIMITATIONS
    assert result["check_count"] == len(result["checks"])
    assert result["error_count"] == 0
    assert result["warning_count"] == len(result["warnings"])
    assert result["errors"] == []


def test_verification_checks_have_stable_ids_order_and_shape(tmp_path):
    packet = make_packet(tmp_path)

    result = verify_packet(packet)

    assert [check["check_id"] for check in result["checks"]] == REQUIRED_VERIFICATION_CHECK_IDS
    for check in result["checks"]:
        assert set(check) == {"check_id", "status", "details"}
        assert check["status"] in {CHECK_STATUS_PASSED, CHECK_STATUS_FAILED}
        assert isinstance(check["details"], list)


def test_verification_result_has_stable_failed_contract(tmp_path):
    packet = make_packet(tmp_path)
    (packet / "retrieval_record.json").unlink()

    result = verify_packet(packet)

    assert result["record_type"] == VERIFICATION_RESULT_RECORD_TYPE
    assert result["verification_status"] == VERIFICATION_STATUS_FAILED
    assert result["verification_scope"] == VERIFICATION_SCOPE
    assert result["packet_dir"] == str(packet)
    assert result["authority_flags"] == AUTHORITY_FLAGS
    assert result["authority_note"] == VERIFICATION_AUTHORITY_NOTE
    assert result["limitations"] == VERIFICATION_LIMITATIONS
    assert result["check_count"] == len(result["checks"])
    assert result["error_count"] == len(result["errors"])
    assert result["error_count"] > 0
    assert "retrieval_record.json" in result["errors"]


def test_verification_result_does_not_claim_validation_or_promotion(tmp_path):
    packet = make_packet(tmp_path)

    result = verify_packet(packet)
    result_text = " ".join(
        [
            result["verification_scope"],
            result["authority_note"],
            *result["limitations"],
        ]
    ).lower()

    assert "scientific validation" in result_text
    assert "does_not_promote_state" in result["limitations"]
    assert result["authority_flags"] == {
        "correctness_proven": False,
        "repo_mutated": False,
        "state_promoted": False,
        "source_control_touched": False,
    }
