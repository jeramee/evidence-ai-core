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
