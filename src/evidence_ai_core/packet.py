from __future__ import annotations

from pathlib import Path
import json

from .ids import make_packet_id, utc_now_iso
from . import records
from .environment import capture_environment
from .hashes import sha256_file
from .constants import REQUIRED_ARTIFACTS, AUTHORITY_FLAGS

def create_static_packet(request_text: str, source_paths: list[str], output_root: str | Path = "evidence_packets") -> Path:
    created_at = utc_now_iso()
    source_paths = [str(Path(p)) for p in source_paths]
    packet_id = make_packet_id(request_text, created_at)
    packet_dir = Path(output_root) / packet_id
    packet_dir.mkdir(parents=True, exist_ok=False)

    _write_json(packet_dir / "query_job.json", records.query_job(packet_id, request_text, source_paths, created_at))
    _write_json(packet_dir / "retrieval_record.json", records.retrieval_record(packet_id, source_paths))
    _write_json(packet_dir / "source_citations.json", records.source_citations(packet_id, source_paths))
    (packet_dir / "context_pack.md").write_text(records.context_pack(packet_id, request_text, source_paths), encoding="utf-8")
    _write_json(packet_dir / "notebook_run_record.json", records.notebook_run_record(packet_id))
    _write_json(packet_dir / "environment_report.json", capture_environment(packet_id))
    _write_json(packet_dir / "replay_manifest.json", records.replay_manifest(packet_id))
    _write_json(packet_dir / "artifact_manifest.json", _artifact_manifest(packet_dir, packet_id, created_at))
    # Re-write manifest after its own hash can be computed as a current file.
    _write_json(packet_dir / "artifact_manifest.json", _artifact_manifest(packet_dir, packet_id, created_at))
    return packet_dir

def _artifact_manifest(packet_dir: Path, packet_id: str, created_at: str) -> dict:
    artifacts = []
    for name in REQUIRED_ARTIFACTS:
        path = packet_dir / name
        exists = path.exists()
        hash_value = None if name == "artifact_manifest.json" else (sha256_file(path) if exists else None)
        artifacts.append({
            "artifact_id": f"artifact_{name.replace('.', '_')}",
            "path": name,
            "artifact_type": "json_record" if name.endswith(".json") else "markdown",
            "role": name.replace(".", "_"),
            "required": True,
            "exists": exists,
            "hash": {"algorithm": "sha256", "value": hash_value},
        })
    return {
        "schema_version": "0.1",
        "record_type": "artifact_manifest",
        "packet_id": packet_id,
        "artifact_manifest_id": f"artifacts_{packet_id}",
        "created_at": created_at,
        "artifact_status": "manifest_complete_for_required_packet_files",
        "artifacts": artifacts,
        "authority_flags": dict(AUTHORITY_FLAGS),
    }

def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
