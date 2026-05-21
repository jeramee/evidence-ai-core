from __future__ import annotations

from pathlib import Path
from .constants import AUTHORITY_FLAGS, REQUIRED_ARTIFACTS
from .ids import utc_now_iso

def query_job(packet_id: str, request_text: str, source_paths: list[str], created_at: str) -> dict:
    return {
        "schema_version": "0.1",
        "record_type": "query_job",
        "packet_id": packet_id,
        "job_id": f"job_{packet_id}",
        "created_at": created_at,
        "requested_by": "local_user",
        "request_text": request_text,
        "job_kind": "static_evidence_packet",
        "input_refs": [{"path": str(path), "kind": "local_source"} for path in source_paths],
        "authority_flags": dict(AUTHORITY_FLAGS),
        "status": "created",
    }

def retrieval_record(packet_id: str, source_paths: list[str]) -> dict:
    results = []
    for idx, source in enumerate(source_paths, start=1):
        results.append({
            "result_id": f"result_{idx:03d}",
            "source_id": f"source_{idx:03d}",
            "rank": idx,
            "score": None,
            "locator": {"path": str(source)},
            "text_preview": _preview(source),
        })
    return {
        "schema_version": "0.1",
        "record_type": "retrieval_record",
        "packet_id": packet_id,
        "retrieval_id": f"retrieval_{packet_id}",
        "retrieval_mode": "static_local_fixture",
        "query_ref": {"path": "query_job.json"},
        "index_ref": None,
        "retriever": {"name": "none", "version": None},
        "parameters": {},
        "results": results,
        "retrieval_status": "static_complete",
        "authority_note": "Static fixture selection does not measure retrieval quality.",
    }

def source_citations(packet_id: str, source_paths: list[str]) -> dict:
    citations = []
    for idx, source in enumerate(source_paths, start=1):
        citations.append({
            "citation_id": f"citation_{idx:03d}",
            "source_id": f"source_{idx:03d}",
            "source_title": Path(source).name,
            "source_type": "local_file",
            "locator": {"path": str(source)},
            "retrieval_result_ref": f"result_{idx:03d}",
            "quoted_or_referenced_text": _preview(source),
            "status": "locator_recorded",
            "support_status": "not_evaluated",
            "authority_note": "Citation locator does not prove claim support.",
        })
    return {
        "schema_version": "0.1",
        "record_type": "source_citations",
        "packet_id": packet_id,
        "citation_set_id": f"citations_{packet_id}",
        "citation_status": "citation_records_present",
        "citations": citations,
    }

def context_pack(packet_id: str, request_text: str, source_paths: list[str]) -> str:
    lines = [
        "# Context Pack",
        "",
        "## Packet",
        f"- Packet ID: {packet_id}",
        "- Context status: static_fixture_context",
        "",
        "## Request Summary",
        request_text,
        "",
        "## Retrieval Summary",
        "Static local source fixture selection. No txtai, model, notebook, or network call occurred.",
        "",
        "## Selected Source Excerpts",
    ]
    for idx, source in enumerate(source_paths, start=1):
        lines.extend(["", f"### citation_{idx:03d} - {Path(source).name}", _preview(source)])
    lines.extend([
        "",
        "## Known Gaps",
        "- Static fixture packet; no real retrieval quality measurement.",
        "- Citation support has not been domain-reviewed.",
        "",
        "## Authority Boundary",
        "This context pack records selected evidence. It does not prove correctness, validation, promotion, or citation support.",
        "",
    ])
    return "\n".join(lines)

def notebook_run_record(packet_id: str) -> dict:
    return {
        "schema_version": "0.1",
        "record_type": "notebook_run_record",
        "packet_id": packet_id,
        "run_id": f"run_{packet_id}",
        "execution_mode": "none_static_v0_1",
        "executor": {"name": "evidence-ai-core", "version": "0.1.0a0", "execution_backend": "none"},
        "started_at": None,
        "completed_at": None,
        "execution_status": "not_executed",
        "inputs": [{"input_id": "context_pack", "path": "context_pack.md", "role": "human_readable_context"}],
        "outputs": [],
        "authority_flags": dict(AUTHORITY_FLAGS),
    }

def replay_manifest(packet_id: str) -> dict:
    return {
        "schema_version": "0.1",
        "record_type": "replay_manifest",
        "packet_id": packet_id,
        "replay_id": f"replay_{packet_id}",
        "replay_status": "inspection_only",
        "replay_scope": "static_packet_verification",
        "required_files": list(REQUIRED_ARTIFACTS),
        "verification_checks": [
            "required_files_exist",
            "json_files_parse",
            "required_fields_present",
            "authority_flags_not_escalated",
            "artifact_hashes_match",
        ],
        "limitations": [
            "No notebook execution is replayed.",
            "No retrieval engine is replayed.",
            "No model output is regenerated.",
        ],
    }

def _preview(path: str, limit: int = 240) -> str:
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace").strip()
    except FileNotFoundError:
        return ""
    return " ".join(text.split())[:limit]
