import json
from pathlib import Path

from evidence_ai_core import create_static_packet
from evidence_ai_core.verify import REQUIRED_FIELDS_BY_ARTIFACT


SCHEMA_DIR = Path("schemas")

SCHEMA_BY_ARTIFACT = {
    "query_job.json": "query_job.schema.json",
    "retrieval_record.json": "retrieval_record.schema.json",
    "source_citations.json": "source_citations.schema.json",
    "notebook_run_record.json": "notebook_run_record.schema.json",
    "environment_report.json": "environment_report.schema.json",
    "artifact_manifest.json": "artifact_manifest.schema.json",
    "replay_manifest.json": "replay_manifest.schema.json",
}


def make_packet(tmp_path: Path) -> Path:
    source = tmp_path / "source.md"
    source.write_text("# Source\nEvidence text.", encoding="utf-8")
    return create_static_packet("schema contract request", [str(source)], tmp_path / "packets")


def load_schema(artifact_name: str) -> dict:
    schema_path = SCHEMA_DIR / SCHEMA_BY_ARTIFACT[artifact_name]
    return json.loads(schema_path.read_text(encoding="utf-8"))


def assert_minimum_schema_match(record: dict, schema: dict) -> None:
    assert schema["type"] == "object"

    for field in schema["required"]:
        assert field in record

    for field, rules in schema.get("properties", {}).items():
        if field not in record:
            continue

        value = record[field]

        if "const" in rules:
            assert value == rules["const"]

        expected_type = rules.get("type")
        if expected_type is None:
            continue

        expected_types = expected_type if isinstance(expected_type, list) else [expected_type]
        assert any(_matches_json_type(value, candidate) for candidate in expected_types), (
            field,
            value,
            expected_types,
        )


def _matches_json_type(value, json_type: str) -> bool:
    if json_type == "object":
        return isinstance(value, dict)
    if json_type == "array":
        return isinstance(value, list)
    if json_type == "string":
        return isinstance(value, str)
    if json_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if json_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if json_type == "boolean":
        return isinstance(value, bool)
    if json_type == "null":
        return value is None
    raise AssertionError(f"Unsupported JSON schema type in static contract test: {json_type}")


def test_schema_files_exist_for_all_json_artifacts():
    for schema_file in SCHEMA_BY_ARTIFACT.values():
        assert (SCHEMA_DIR / schema_file).exists()


def test_schema_required_fields_track_verifier_contract():
    for artifact_name, required_fields in REQUIRED_FIELDS_BY_ARTIFACT.items():
        schema = load_schema(artifact_name)
        assert set(required_fields).issubset(set(schema["required"]))


def test_generated_static_packet_records_match_minimum_schema_contract(tmp_path):
    packet = make_packet(tmp_path)

    for artifact_name in SCHEMA_BY_ARTIFACT:
        record = json.loads((packet / artifact_name).read_text(encoding="utf-8"))
        schema = load_schema(artifact_name)

        assert_minimum_schema_match(record, schema)
