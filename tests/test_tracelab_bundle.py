import hashlib
import json
import zipfile
from pathlib import Path

from evidence_ai_core.cli import main
from evidence_ai_core.tracelab_bundle import preview_tracelab_bundle


BOUNDARY_NOTES = [
    "evidence != truth",
    "operational validation != scientific validity",
    "approval record != agent permission",
    "dry-run != physical execution",
    "NeuML handoff != claim promotion",
    "simulated adapter != hardware adapter",
]


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_fake_tracelab_bundle(tmp_path: Path) -> Path:
    bundle_path = tmp_path / "trace_lab_export.zip"
    run_manifest = b'{"record_type":"trace_lab_run_manifest"}\n'
    validation_result = b'{"validation_status":"passed_operational_checks"}\n'

    manifest = {
        "record_type": "trace_lab_export_manifest",
        "export_scope": "operational_simulation_only",
        "export_status": "ready_for_local_zip_export",
        "source_validation_status": "passed_operational_checks",
        "bundle_manifest_path": "trace_lab_export_manifest.json",
        "bundle_file_count": 2,
        "bundle_files": [
            {
                "path": "run_manifest.json",
                "size_bytes": len(run_manifest),
                "hash": _hash_bytes(run_manifest),
            },
            {
                "path": "validation_result.json",
                "size_bytes": len(validation_result),
                "hash": _hash_bytes(validation_result),
            },
        ],
        "authority_flags": {
            "agent_approved": False,
            "physical_execution_completed": False,
            "scientific_truth_validated": False,
            "state_promoted": False,
            "claims_promoted": False,
            "network_calls_performed": False,
            "package_installation_performed": False,
            "hardware_access_performed": False,
        },
        "boundary_notes": BOUNDARY_NOTES,
    }

    with zipfile.ZipFile(bundle_path, "w") as bundle:
        bundle.writestr("run_manifest.json", run_manifest)
        bundle.writestr("validation_result.json", validation_result)
        bundle.writestr(
            "trace_lab_export_manifest.json",
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        )

    return bundle_path


def test_tracelab_bundle_preview_passes_for_valid_export_bundle(tmp_path):
    bundle_path = _write_fake_tracelab_bundle(tmp_path)

    result = preview_tracelab_bundle(str(bundle_path))

    assert result["record_type"] == "tracelab_bundle_preview"
    assert result["preview_status"] == "passed_tracelab_bundle_preview"
    assert result["trace_lab_record_type"] == "trace_lab_export_manifest"
    assert result["trace_lab_export_scope"] == "operational_simulation_only"
    assert result["trace_lab_source_validation_status"] == "passed_operational_checks"
    assert result["extraction_performed"] is False
    assert result["execution_performed"] is False
    assert result["network_calls_performed"] is False
    assert result["hardware_access_performed"] is False
    assert result["claims_promoted"] is False
    assert result["errors"] == []


def test_tracelab_bundle_preview_fails_on_hash_mismatch(tmp_path):
    bundle_path = _write_fake_tracelab_bundle(tmp_path)

    with zipfile.ZipFile(bundle_path, "a") as bundle:
        bundle.writestr("run_manifest.json", b"tampered\n")

    result = preview_tracelab_bundle(str(bundle_path))

    assert result["preview_status"] == "failed_tracelab_bundle_preview"
    assert any("hash mismatch" in error for error in result["errors"])


def test_tracelab_bundle_preview_fails_on_authority_escalation(tmp_path):
    bundle_path = tmp_path / "bad_trace_lab_export.zip"
    payload = b'{"record_type":"trace_lab_run_manifest"}\n'
    manifest = {
        "record_type": "trace_lab_export_manifest",
        "export_scope": "operational_simulation_only",
        "export_status": "ready_for_local_zip_export",
        "source_validation_status": "passed_operational_checks",
        "bundle_manifest_path": "trace_lab_export_manifest.json",
        "bundle_file_count": 1,
        "bundle_files": [
            {
                "path": "run_manifest.json",
                "size_bytes": len(payload),
                "hash": _hash_bytes(payload),
            },
        ],
        "authority_flags": {
            "agent_approved": True,
            "physical_execution_completed": False,
            "scientific_truth_validated": False,
            "state_promoted": False,
            "claims_promoted": False,
            "network_calls_performed": False,
            "package_installation_performed": False,
            "hardware_access_performed": False,
        },
        "boundary_notes": BOUNDARY_NOTES,
    }

    with zipfile.ZipFile(bundle_path, "w") as bundle:
        bundle.writestr("run_manifest.json", payload)
        bundle.writestr("trace_lab_export_manifest.json", json.dumps(manifest))

    result = preview_tracelab_bundle(str(bundle_path))

    assert result["preview_status"] == "failed_tracelab_bundle_preview"
    assert any("authority flag must remain false: agent_approved" in error for error in result["errors"])


def test_tracelab_bundle_preview_fails_on_unsafe_zip_entry(tmp_path):
    bundle_path = tmp_path / "unsafe_trace_lab_export.zip"

    with zipfile.ZipFile(bundle_path, "w") as bundle:
        bundle.writestr("../evil.txt", "bad")

    result = preview_tracelab_bundle(str(bundle_path))

    assert result["preview_status"] == "failed_tracelab_bundle_preview"
    assert any("unsafe zip entry" in error for error in result["errors"])


def test_cli_tracelab_bundle_preview_outputs_readonly_result(tmp_path, capsys):
    bundle_path = _write_fake_tracelab_bundle(tmp_path)

    status = main(["tracelab-bundle-preview", str(bundle_path)])
    result = json.loads(capsys.readouterr().out)

    assert status == 0
    assert result["record_type"] == "tracelab_bundle_preview"
    assert result["preview_status"] == "passed_tracelab_bundle_preview"
    assert result["extraction_performed"] is False
    assert result["execution_performed"] is False
    assert "does not validate scientific truth" in result["authority_note"]
