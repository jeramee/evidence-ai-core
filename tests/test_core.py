import json
from pathlib import Path
from evidence_ai_core import create_static_packet, verify_packet

def test_create_and_verify_static_packet(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("# Source\nEvidence text.", encoding="utf-8")
    packet = create_static_packet("demo request", [str(source)], tmp_path / "packets")
    required = [
        "query_job.json",
        "retrieval_record.json",
        "source_citations.json",
        "context_pack.md",
        "notebook_run_record.json",
        "environment_report.json",
        "artifact_manifest.json",
        "replay_manifest.json",
    ]
    for name in required:
        assert (packet / name).exists()
    result = verify_packet(packet)
    assert result["verification_status"] == "passed_mechanical_checks"

def test_verifier_fails_on_authority_escalation(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("evidence", encoding="utf-8")
    packet = create_static_packet("demo request", [str(source)], tmp_path / "packets")
    run = json.loads((packet / "notebook_run_record.json").read_text(encoding="utf-8"))
    run["authority_flags"]["correctness_proven"] = True
    (packet / "notebook_run_record.json").write_text(json.dumps(run), encoding="utf-8")
    result = verify_packet(packet)
    assert result["verification_status"] == "failed_mechanical_checks"
    assert any(c["check_id"] == "authority_flags_not_escalated" and c["status"] == "failed" for c in result["checks"])
