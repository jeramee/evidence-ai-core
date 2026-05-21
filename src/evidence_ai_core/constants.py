REQUIRED_ARTIFACTS = [
    "query_job.json",
    "retrieval_record.json",
    "source_citations.json",
    "context_pack.md",
    "notebook_run_record.json",
    "environment_report.json",
    "artifact_manifest.json",
    "replay_manifest.json",
]

JSON_ARTIFACTS = [name for name in REQUIRED_ARTIFACTS if name.endswith(".json")]

AUTHORITY_FLAGS = {
    "correctness_proven": False,
    "repo_mutated": False,
    "state_promoted": False,
    "source_control_touched": False,
}

EXPECTED_RECORD_TYPES = {
    "query_job.json": "query_job",
    "retrieval_record.json": "retrieval_record",
    "source_citations.json": "source_citations",
    "notebook_run_record.json": "notebook_run_record",
    "environment_report.json": "environment_report",
    "artifact_manifest.json": "artifact_manifest",
    "replay_manifest.json": "replay_manifest",
}

CHECK_STATUS_PASSED = "passed"
CHECK_STATUS_FAILED = "failed"

VERIFICATION_RESULT_RECORD_TYPE = "verification_result"
VERIFICATION_STATUS_PASSED = "passed_mechanical_checks"
VERIFICATION_STATUS_FAILED = "failed_mechanical_checks"
VERIFICATION_SCOPE = "mechanical_packet_shape_only"
VERIFICATION_AUTHORITY_NOTE = "Mechanical verification is not scientific validation."

REQUIRED_VERIFICATION_CHECK_IDS = [
    "required_files_exist",
    "json_files_parse",
    "required_fields_present",
    "packet_id_consistent",
    "authority_flags_not_escalated",
    "artifact_hashes_match",
]

VERIFICATION_LIMITATIONS = [
    "does_not_prove_scientific_correctness",
    "does_not_validate_source_claims",
    "does_not_execute_notebooks_or_models",
    "does_not_touch_source_control",
    "does_not_promote_state",
]
