from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .constants import (
    EXPECTED_RECORD_TYPES,
    JSON_ARTIFACTS,
    VERIFICATION_AUTHORITY_NOTE,
    VERIFICATION_LIMITATIONS,
)
from .errors import PacketInputError, PacketReadError


SCHEMA_INDEX_RECORD_TYPE = "schema_index"
SCHEMA_CONTRACT_RECORD_TYPE = "schema_contract"
SCHEMA_SCOPE = "static_json_artifact_contracts_only"
SCHEMA_DRAFT = "https://json-schema.org/draft/2020-12/schema"


def list_schema_contracts(schema_dir: str | Path | None = None) -> dict[str, Any]:
    """Discover static JSON Schema contracts for packet JSON artifacts.

    This is static/local schema discovery only. It does not validate scientific
    claims, execute packet artifacts, contact external services, or promote
    state.
    """
    resolved_schema_dir = _resolve_schema_dir(schema_dir)
    schema_entries: list[dict[str, Any]] = []
    missing_schema_files: list[str] = []

    for artifact_name in JSON_ARTIFACTS:
        schema_file = _schema_file_for_artifact(artifact_name)
        schema_path = resolved_schema_dir / schema_file

        if not schema_path.exists():
            missing_schema_files.append(schema_file)
            continue

        schema = _read_schema(schema_path)
        schema_entries.append(_schema_entry(artifact_name, schema_file, schema))

    return {
        "schema_version": "0.1",
        "record_type": SCHEMA_INDEX_RECORD_TYPE,
        "schema_scope": SCHEMA_SCOPE,
        "schema_dir": str(resolved_schema_dir),
        "schema_count": len(schema_entries),
        "artifact_count": len(JSON_ARTIFACTS),
        "missing_schema_files": missing_schema_files,
        "schemas": schema_entries,
        "authority_note": _schema_authority_note(),
        "limitations": _schema_limitations(),
    }


def load_schema_contract(
    artifact_or_schema: str,
    schema_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Load one static schema contract by artifact name or schema filename."""
    resolved_schema_dir = _resolve_schema_dir(schema_dir)
    artifact_name, schema_file = _normalize_schema_request(artifact_or_schema)
    schema_path = resolved_schema_dir / schema_file

    if not schema_path.exists():
        raise PacketInputError(f"schema file does not exist: {schema_file}")

    schema = _read_schema(schema_path)
    return {
        "schema_version": "0.1",
        "record_type": SCHEMA_CONTRACT_RECORD_TYPE,
        "schema_scope": SCHEMA_SCOPE,
        "artifact": artifact_name,
        "schema_file": schema_file,
        "schema_path": str(schema_path),
        "schema": schema,
        "required_fields": list(schema.get("required", [])),
        "property_names": sorted((schema.get("properties") or {}).keys()),
        "expected_record_type": _expected_record_type(schema, artifact_name),
        "authority_note": _schema_authority_note(),
        "limitations": _schema_limitations(),
    }


def _schema_entry(artifact_name: str, schema_file: str, schema: dict[str, Any]) -> dict[str, Any]:
    properties = schema.get("properties") or {}
    authority_flags = properties.get("authority_flags")

    return {
        "artifact": artifact_name,
        "schema_file": schema_file,
        "title": schema.get("title"),
        "draft": schema.get("$schema"),
        "expected_record_type": _expected_record_type(schema, artifact_name),
        "required_fields": list(schema.get("required", [])),
        "required_field_count": len(schema.get("required", [])),
        "property_names": sorted(properties.keys()),
        "property_count": len(properties),
        "has_authority_flags_contract": isinstance(authority_flags, dict),
    }


def _read_schema(schema_path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PacketReadError(f"{schema_path.name}: invalid JSON: {exc}") from exc

    if not isinstance(loaded, dict):
        raise PacketReadError(f"{schema_path.name}: schema JSON must be an object")

    return loaded


def _normalize_schema_request(artifact_or_schema: str) -> tuple[str, str]:
    value = artifact_or_schema.strip()
    if not value:
        raise PacketInputError("schema artifact or filename must not be empty")

    if value.endswith(".schema.json"):
        artifact_name = value.removesuffix(".schema.json") + ".json"
        schema_file = value
    elif value.endswith(".json"):
        artifact_name = value
        schema_file = _schema_file_for_artifact(value)
    else:
        artifact_name = value + ".json"
        schema_file = value + ".schema.json"

    if artifact_name not in JSON_ARTIFACTS:
        raise PacketInputError(f"unknown schema artifact: {artifact_or_schema}")

    return artifact_name, schema_file


def _schema_file_for_artifact(artifact_name: str) -> str:
    return artifact_name.removesuffix(".json") + ".schema.json"


def _expected_record_type(schema: dict[str, Any], artifact_name: str) -> str | None:
    properties = schema.get("properties") or {}
    record_type = properties.get("record_type") or {}

    if isinstance(record_type, dict) and "const" in record_type:
        return record_type["const"]

    return EXPECTED_RECORD_TYPES.get(artifact_name)


def _resolve_schema_dir(schema_dir: str | Path | None) -> Path:
    if schema_dir is not None:
        candidates = [Path(schema_dir)]
    else:
        package_schema_dir = Path(__file__).resolve().parent / "schemas"
        source_tree_schema_dir = Path(__file__).resolve().parents[2] / "schemas"
        cwd_schema_dir = Path.cwd() / "schemas"
        candidates = [package_schema_dir, source_tree_schema_dir, cwd_schema_dir]

    for candidate in candidates:
        if candidate.exists():
            if not candidate.is_dir():
                raise PacketInputError(f"schema path is not a directory: {candidate}")
            return candidate

    missing = ", ".join(str(candidate) for candidate in candidates)
    raise PacketInputError(f"schema directory does not exist; checked: {missing}")


def _schema_authority_note() -> str:
    return f"Schema contracts are static shape contracts only. {VERIFICATION_AUTHORITY_NOTE}"


def _schema_limitations() -> list[str]:
    return [
        "does_not_validate_json_instances_at_runtime",
        "does_not_prove_scientific_correctness",
        *VERIFICATION_LIMITATIONS,
    ]
