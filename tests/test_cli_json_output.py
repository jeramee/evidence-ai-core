import json
from pathlib import Path

from evidence_ai_core.cli import main


def make_source(tmp_path: Path) -> Path:
    source = tmp_path / "source.md"
    source.write_text("# Source\nEvidence text.", encoding="utf-8")
    return source


def create_packet_with_cli(tmp_path: Path, capsys) -> Path:
    source = make_source(tmp_path)
    output_root = tmp_path / "packets"

    status = main(
        [
            "create-static",
            "--request-text",
            "cli json output request",
            "--source",
            str(source),
            "--output-root",
            str(output_root),
        ]
    )
    packet_dir = Path(capsys.readouterr().out.strip())

    assert status == 0
    assert packet_dir.exists()
    return packet_dir


def assert_compact_stable_json(raw: str) -> dict:
    assert raw.endswith("\n")
    assert len(raw.splitlines()) == 1
    assert "\n  " not in raw
    assert ": " not in raw

    parsed = json.loads(raw)
    assert raw == json.dumps(parsed, sort_keys=True, separators=(",", ":")) + "\n"
    return parsed


def assert_pretty_stable_json(raw: str) -> dict:
    assert raw.endswith("\n")
    assert len(raw.splitlines()) > 1
    assert "\n  " in raw
    assert ": " in raw

    parsed = json.loads(raw)
    assert raw == json.dumps(parsed, indent=2, sort_keys=True) + "\n"
    return parsed


def test_cli_json_output_is_compact_by_default_for_verify(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)

    status = main(["verify", str(packet_dir)])
    raw = capsys.readouterr().out
    result = assert_compact_stable_json(raw)

    assert status == 0
    assert result["verification_status"] == "passed_mechanical_checks"


def test_cli_json_pretty_option_emits_indented_json_for_verify(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)

    status = main(["verify", str(packet_dir), "--pretty"])
    raw = capsys.readouterr().out
    result = assert_pretty_stable_json(raw)

    assert status == 0
    assert result["verification_status"] == "passed_mechanical_checks"


def test_cli_json_output_is_compact_by_default_for_static_discovery_commands(capsys):
    status = main(["schema-index"])
    raw = capsys.readouterr().out
    result = assert_compact_stable_json(raw)

    assert status == 0
    assert result["record_type"] == "schema_index"


def test_cli_json_pretty_option_works_for_static_discovery_commands(capsys):
    status = main(["schema-contract", "query_job.json", "--pretty"])
    raw = capsys.readouterr().out
    result = assert_pretty_stable_json(raw)

    assert status == 0
    assert result["record_type"] == "schema_contract"
    assert result["artifact"] == "query_job.json"


def test_cli_json_output_is_compact_by_default_for_packet_summary_commands(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)

    commands = [
        ["inspect", str(packet_dir)],
        ["summary", str(packet_dir)],
        ["manifest", str(packet_dir)],
        ["hash-summary", str(packet_dir)],
    ]

    for command in commands:
        status = main(command)
        raw = capsys.readouterr().out
        result = assert_compact_stable_json(raw)

        assert status == 0
        assert isinstance(result["record_type"], str)


def test_cli_json_output_is_compact_by_default_for_zip_import_preview(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)
    output_zip = tmp_path / "packet.zip"

    export_status = main(["export-zip", str(packet_dir), "--output-zip", str(output_zip)])
    capsys.readouterr()
    assert export_status == 0

    status = main(["import-zip-preview", str(output_zip)])
    raw = capsys.readouterr().out
    result = assert_compact_stable_json(raw)

    assert status == 0
    assert result["record_type"] == "packet_zip_import_preview_result"


def test_cli_json_pretty_option_works_for_zip_import_preview(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)
    output_zip = tmp_path / "packet.zip"

    export_status = main(["export-zip", str(packet_dir), "--output-zip", str(output_zip)])
    capsys.readouterr()
    assert export_status == 0

    status = main(["import-zip-preview", str(output_zip), "--pretty"])
    raw = capsys.readouterr().out
    result = assert_pretty_stable_json(raw)

    assert status == 0
    assert result["record_type"] == "packet_zip_import_preview_result"



def test_cli_json_output_is_compact_by_default_for_zip_import_extract(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)
    output_zip = tmp_path / "packet.zip"
    output_root = tmp_path / "imports"
    output_root.mkdir()

    export_status = main(["export-zip", str(packet_dir), "--output-zip", str(output_zip)])
    capsys.readouterr()
    assert export_status == 0

    status = main(["import-zip-extract", str(output_zip), "--output-root", str(output_root)])
    raw = capsys.readouterr().out
    result = assert_compact_stable_json(raw)

    assert status == 0
    assert result["record_type"] == "packet_zip_import_result"


def test_cli_json_pretty_option_works_for_zip_import_extract(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)
    output_zip = tmp_path / "packet.zip"
    output_root = tmp_path / "imports"
    output_root.mkdir()

    export_status = main(["export-zip", str(packet_dir), "--output-zip", str(output_zip)])
    capsys.readouterr()
    assert export_status == 0

    status = main(["import-zip-extract", str(output_zip), "--output-root", str(output_root), "--pretty"])
    raw = capsys.readouterr().out
    result = assert_pretty_stable_json(raw)

    assert status == 0
    assert result["record_type"] == "packet_zip_import_result"


def test_cli_json_output_is_compact_by_default_for_bundle_inventory(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)
    output_zip = tmp_path / "packet.zip"

    export_status = main(["export-zip", str(packet_dir), "--output-zip", str(output_zip)])
    capsys.readouterr()
    assert export_status == 0

    status = main(["bundle-inventory", str(tmp_path)])
    raw = capsys.readouterr().out
    result = assert_compact_stable_json(raw)

    assert status == 0
    assert result["record_type"] == "packet_bundle_inventory"


def test_cli_json_pretty_option_works_for_bundle_inventory(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)
    output_zip = tmp_path / "packet.zip"

    export_status = main(["export-zip", str(packet_dir), "--output-zip", str(output_zip)])
    capsys.readouterr()
    assert export_status == 0

    status = main(["bundle-inventory", str(tmp_path), "--pretty"])
    raw = capsys.readouterr().out
    result = assert_pretty_stable_json(raw)

    assert status == 0
    assert result["record_type"] == "packet_bundle_inventory"


def test_cli_json_output_is_compact_by_default_for_bundle_inventory_jsonl(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)
    output_zip = tmp_path / "packet.zip"
    output_jsonl = tmp_path / "inventory.jsonl"

    export_status = main(["export-zip", str(packet_dir), "--output-zip", str(output_zip)])
    capsys.readouterr()
    assert export_status == 0

    status = main(["bundle-inventory-jsonl", str(tmp_path), "--output-jsonl", str(output_jsonl)])
    raw = capsys.readouterr().out
    result = assert_compact_stable_json(raw)

    assert status == 0
    assert result["record_type"] == "packet_bundle_inventory_jsonl_export"
    assert output_jsonl.exists()


def test_cli_json_pretty_option_works_for_bundle_inventory_jsonl(tmp_path, capsys):
    packet_dir = create_packet_with_cli(tmp_path, capsys)
    output_zip = tmp_path / "packet.zip"
    output_jsonl = tmp_path / "inventory.jsonl"

    export_status = main(["export-zip", str(packet_dir), "--output-zip", str(output_zip)])
    capsys.readouterr()
    assert export_status == 0

    status = main(["bundle-inventory-jsonl", str(tmp_path), "--output-jsonl", str(output_jsonl), "--pretty"])
    raw = capsys.readouterr().out
    result = assert_pretty_stable_json(raw)

    assert status == 0
    assert result["record_type"] == "packet_bundle_inventory_jsonl_export"
    assert output_jsonl.exists()
