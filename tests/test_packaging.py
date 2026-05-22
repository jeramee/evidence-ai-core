import json
import os
from pathlib import Path

from evidence_ai_core.schema_index import list_schema_contracts


REPO_ROOT = Path(__file__).resolve().parents[1]
ROOT_SCHEMA_DIR = REPO_ROOT / "schemas"
PACKAGE_SCHEMA_DIR = REPO_ROOT / "src" / "evidence_ai_core" / "schemas"
PYPROJECT = REPO_ROOT / "pyproject.toml"


def test_pyproject_declares_cli_entry_point_and_schema_package_data():
    pyproject_text = PYPROJECT.read_text(encoding="utf-8")

    assert 'evidence-ai-core = "evidence_ai_core.cli:main"' in pyproject_text
    assert "[tool.setuptools.package-data]" in pyproject_text
    assert 'evidence_ai_core = ["schemas/*.schema.json"]' in pyproject_text


def test_package_schema_data_mirrors_root_schema_contracts():
    root_schema_names = sorted(path.name for path in ROOT_SCHEMA_DIR.glob("*.schema.json"))
    package_schema_names = sorted(path.name for path in PACKAGE_SCHEMA_DIR.glob("*.schema.json"))

    assert root_schema_names == [
        "artifact_manifest.schema.json",
        "environment_report.schema.json",
        "notebook_run_record.schema.json",
        "query_job.schema.json",
        "replay_manifest.schema.json",
        "retrieval_record.schema.json",
        "source_citations.schema.json",
    ]
    assert package_schema_names == root_schema_names

    for schema_name in root_schema_names:
        root_schema = json.loads((ROOT_SCHEMA_DIR / schema_name).read_text(encoding="utf-8"))
        package_schema = json.loads((PACKAGE_SCHEMA_DIR / schema_name).read_text(encoding="utf-8"))
        assert package_schema == root_schema


def test_schema_discovery_uses_packaged_schema_data_when_cwd_has_no_schemas(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = list_schema_contracts()

    assert result["record_type"] == "schema_index"
    assert result["schema_count"] == 7
    assert result["missing_schema_files"] == []
    assert Path(result["schema_dir"]).name == "schemas"
    assert Path(result["schema_dir"]).parent.name == "evidence_ai_core"
