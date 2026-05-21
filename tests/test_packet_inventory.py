import json
from pathlib import Path

import pytest

from evidence_ai_core import create_static_packet, export_packet_inventory_jsonl, export_packet_zip, inventory_packet_bundle
from evidence_ai_core.errors import PacketInputError
from evidence_ai_core.cli import main


def make_source(tmp_path: Path) -> Path:
    source = tmp_path / "source.md"
    source.write_text("# Source\nEvidence text.", encoding="utf-8")
    return source


def make_packet(root: Path, request_text: str = "inventory request") -> Path:
    source = root / "source.md"
    source.write_text("# Source\nEvidence text.", encoding="utf-8")
    return create_static_packet(request_text, [str(source)], root / "packets")


def test_inventory_packet_bundle_returns_static_inventory_contract(tmp_path):
    packet_dir = make_packet(tmp_path)
    output_zip = tmp_path / "packet.zip"
    export_packet_zip(packet_dir, output_zip)

    inventory = inventory_packet_bundle(tmp_path)

    assert inventory["schema_version"] == "0.1"
    assert inventory["record_type"] == "packet_bundle_inventory"
    assert inventory["root_path"] == str(tmp_path)
    assert inventory["inventory_scope"] == "static_local_packet_bundle_inventory"
    assert inventory["inventory_status"] == "completed"
    assert inventory["verification_status"] == "passed_mechanical_checks"
    assert inventory["recursive"] is False
    assert inventory["include_zips"] is True
    assert inventory["packet_dir_count"] == 0
    assert inventory["packet_zip_count"] == 1
    assert inventory["candidate_count"] == 1
    assert inventory["failed_candidate_count"] == 0
    assert inventory["packet_dirs"] == []
    assert inventory["packet_zips"][0]["kind"] == "packet_zip"
    assert inventory["packet_zips"][0]["packet_id"] == packet_dir.name
    assert inventory["packet_zips"][0]["verification_status"] == "passed_mechanical_checks"
    assert "Evidence is not proof" in inventory["authority_note"]


def test_inventory_packet_bundle_reports_packet_dirs_when_root_contains_packets(tmp_path):
    bundle_root = tmp_path / "bundle"
    bundle_root.mkdir()
    packet_dir = create_static_packet("inventory request", [str(make_source(tmp_path))], bundle_root)

    inventory = inventory_packet_bundle(bundle_root)

    assert inventory["packet_dir_count"] == 1
    assert inventory["packet_zip_count"] == 0
    assert inventory["candidate_count"] == 1
    packet_entry = inventory["packet_dirs"][0]
    assert packet_entry["kind"] == "packet_dir"
    assert packet_entry["packet_id"] == packet_dir.name
    assert packet_entry["relative_path"] == packet_dir.name
    assert packet_entry["verification_status"] == "passed_mechanical_checks"
    assert packet_entry["missing_required_artifact_count"] == 0


def test_inventory_packet_bundle_reports_failed_packet_candidates_without_throwing(tmp_path):
    bundle_root = tmp_path / "bundle"
    bundle_root.mkdir()
    packet_dir = create_static_packet("inventory failure request", [str(make_source(tmp_path))], bundle_root)
    (packet_dir / "retrieval_record.json").unlink()

    inventory = inventory_packet_bundle(bundle_root)

    assert inventory["verification_status"] == "failed_mechanical_checks"
    assert inventory["packet_dir_count"] == 1
    assert inventory["failed_candidate_count"] == 1
    packet_entry = inventory["packet_dirs"][0]
    assert packet_entry["verification_status"] == "failed_mechanical_checks"
    assert packet_entry["missing_required_artifact_count"] == 1
    assert packet_entry["missing_required_artifacts"] == ["retrieval_record.json"]


def test_inventory_packet_bundle_supports_recursive_discovery(tmp_path):
    nested = tmp_path / "nested" / "packets"
    nested.mkdir(parents=True)
    packet_dir = create_static_packet("recursive inventory request", [str(make_source(tmp_path))], nested)
    export_packet_zip(packet_dir, tmp_path / "nested" / "packet.zip")

    shallow = inventory_packet_bundle(tmp_path)
    recursive = inventory_packet_bundle(tmp_path, recursive=True)

    assert shallow["candidate_count"] == 0
    assert recursive["packet_dir_count"] == 1
    assert recursive["packet_zip_count"] == 1
    assert recursive["candidate_count"] == 2
    assert recursive["packet_dirs"][0]["packet_id"] == packet_dir.name
    assert recursive["packet_zips"][0]["packet_id"] == packet_dir.name


def test_inventory_packet_bundle_can_exclude_zips(tmp_path):
    packet_dir = make_packet(tmp_path)
    export_packet_zip(packet_dir, tmp_path / "packet.zip")

    inventory = inventory_packet_bundle(tmp_path, include_zips=False)

    assert inventory["include_zips"] is False
    assert inventory["packet_zip_count"] == 0
    assert inventory["candidate_count"] == 0


def test_inventory_packet_bundle_rejects_missing_root(tmp_path):
    with pytest.raises(PacketInputError, match="inventory root does not exist"):
        inventory_packet_bundle(tmp_path / "missing")


def test_cli_bundle_inventory_emits_static_inventory_result(tmp_path, capsys):
    packet_dir = make_packet(tmp_path)
    export_packet_zip(packet_dir, tmp_path / "packet.zip")

    status = main(["bundle-inventory", str(tmp_path)])
    result = json.loads(capsys.readouterr().out)

    assert status == 0
    assert result["schema_version"] == "0.1"
    assert result["record_type"] == "packet_bundle_inventory"
    assert result["inventory_status"] == "completed"
    assert result["verification_status"] == "passed_mechanical_checks"
    assert result["packet_zip_count"] == 1
    assert result["packet_zips"][0]["packet_id"] == packet_dir.name


def test_inventory_packet_bundle_filters_kind_and_status(tmp_path):
    bundle_root = tmp_path / "bundle"
    bundle_root.mkdir()
    source = make_source(tmp_path)
    passed_packet = create_static_packet("passed inventory request", [str(source)], bundle_root)
    failed_packet = create_static_packet("failed inventory request", [str(source)], bundle_root)
    (failed_packet / "retrieval_record.json").unlink()
    export_packet_zip(passed_packet, bundle_root / "passed.zip")

    inventory = inventory_packet_bundle(
        bundle_root,
        kind_filter="dirs",
        status_filter="failed",
    )

    assert inventory["kind_filter"] == "dirs"
    assert inventory["status_filter"] == "failed"
    assert inventory["sort_by"] == "relative-path"
    assert inventory["sort_reverse"] is False
    assert inventory["unfiltered_candidate_count"] == 3
    assert inventory["candidate_count"] == 1
    assert inventory["packet_dir_count"] == 1
    assert inventory["packet_zip_count"] == 0
    assert inventory["failed_candidate_count"] == 1
    assert inventory["candidates"] == inventory["packet_dirs"]
    assert inventory["packet_dirs"][0]["packet_id"] == failed_packet.name
    assert inventory["packet_dirs"][0]["verification_status"] == "failed_mechanical_checks"


def test_inventory_packet_bundle_sorts_candidates_by_name_and_reverse(tmp_path):
    packet_dir = make_packet(tmp_path)
    export_packet_zip(packet_dir, tmp_path / "beta.zip")
    export_packet_zip(packet_dir, tmp_path / "alpha.zip")

    by_name = inventory_packet_bundle(
        tmp_path,
        kind_filter="zips",
        sort_by="name",
    )
    reversed_by_name = inventory_packet_bundle(
        tmp_path,
        kind_filter="zips",
        sort_by="name",
        reverse=True,
    )

    assert [candidate["name"] for candidate in by_name["candidates"]] == ["alpha.zip", "beta.zip"]
    assert [candidate["name"] for candidate in reversed_by_name["candidates"]] == ["beta.zip", "alpha.zip"]
    assert by_name["packet_zips"] == by_name["candidates"]
    assert reversed_by_name["sort_reverse"] is True


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"kind_filter": "bad-kind"}, "unknown inventory kind filter"),
        ({"status_filter": "bad-status"}, "unknown inventory status filter"),
        ({"sort_by": "bad-sort"}, "unknown inventory sort field"),
    ],
)
def test_inventory_packet_bundle_rejects_unknown_filter_and_sort_options(tmp_path, kwargs, message):
    with pytest.raises(PacketInputError, match=message):
        inventory_packet_bundle(tmp_path, **kwargs)


def test_cli_bundle_inventory_supports_filter_and_sort_options(tmp_path, capsys):
    bundle_root = tmp_path / "bundle"
    bundle_root.mkdir()
    source = make_source(tmp_path)
    passed_packet = create_static_packet("passed cli inventory request", [str(source)], bundle_root)
    failed_packet = create_static_packet("failed cli inventory request", [str(source)], bundle_root)
    (failed_packet / "retrieval_record.json").unlink()
    export_packet_zip(passed_packet, bundle_root / "passed.zip")

    status = main(
        [
            "bundle-inventory",
            str(bundle_root),
            "--kind",
            "dirs",
            "--status",
            "failed",
            "--sort",
            "name",
        ]
    )
    result = json.loads(capsys.readouterr().out)

    assert status == 1
    assert result["kind_filter"] == "dirs"
    assert result["status_filter"] == "failed"
    assert result["sort_by"] == "name"
    assert result["candidate_count"] == 1
    assert result["packet_dirs"][0]["packet_id"] == failed_packet.name



def test_export_packet_inventory_jsonl_writes_filtered_sorted_candidate_lines(tmp_path):
    packet_dir = make_packet(tmp_path)
    export_packet_zip(packet_dir, tmp_path / "beta.zip")
    export_packet_zip(packet_dir, tmp_path / "alpha.zip")
    output_jsonl = tmp_path / "inventory.jsonl"

    result = export_packet_inventory_jsonl(
        tmp_path,
        output_jsonl,
        kind_filter="zips",
        sort_by="name",
    )

    lines = output_jsonl.read_text(encoding="utf-8").splitlines()
    records = [json.loads(line) for line in lines]

    assert result["schema_version"] == "0.1"
    assert result["record_type"] == "packet_bundle_inventory_jsonl_export"
    assert result["export_status"] == "exported"
    assert result["verification_status"] == "passed_mechanical_checks"
    assert result["kind_filter"] == "zips"
    assert result["sort_by"] == "name"
    assert result["candidate_count"] == 2
    assert result["jsonl_record_count"] == 2
    assert result["bytes_written"] == output_jsonl.stat().st_size
    assert [record["name"] for record in records] == ["alpha.zip", "beta.zip"]
    assert all(record["kind"] == "packet_zip" for record in records)
    assert all(line == json.dumps(json.loads(line), sort_keys=True, separators=(",", ":")) for line in lines)
    assert "Evidence is not proof" in result["authority_note"]


def test_export_packet_inventory_jsonl_refuses_overwrite_without_flag(tmp_path):
    output_jsonl = tmp_path / "inventory.jsonl"
    output_jsonl.write_text("existing\n", encoding="utf-8")

    with pytest.raises(Exception, match="output JSONL already exists"):
        export_packet_inventory_jsonl(tmp_path, output_jsonl)


def test_export_packet_inventory_jsonl_allows_overwrite_with_flag(tmp_path):
    output_jsonl = tmp_path / "inventory.jsonl"
    output_jsonl.write_text("existing\n", encoding="utf-8")

    result = export_packet_inventory_jsonl(tmp_path, output_jsonl, overwrite=True)

    assert result["export_status"] == "exported"
    assert result["overwrite"] is True
    assert output_jsonl.read_text(encoding="utf-8") == ""


def test_cli_bundle_inventory_jsonl_emits_export_result_and_writes_jsonl(tmp_path, capsys):
    packet_dir = make_packet(tmp_path)
    export_packet_zip(packet_dir, tmp_path / "packet.zip")
    output_jsonl = tmp_path / "inventory.jsonl"

    status = main(
        [
            "bundle-inventory-jsonl",
            str(tmp_path),
            "--output-jsonl",
            str(output_jsonl),
            "--kind",
            "zips",
            "--sort",
            "name",
        ]
    )
    result = json.loads(capsys.readouterr().out)
    records = [json.loads(line) for line in output_jsonl.read_text(encoding="utf-8").splitlines()]

    assert status == 0
    assert result["record_type"] == "packet_bundle_inventory_jsonl_export"
    assert result["verification_status"] == "passed_mechanical_checks"
    assert result["candidate_count"] == 1
    assert result["jsonl_record_count"] == 1
    assert records[0]["packet_id"] == packet_dir.name
    assert records[0]["kind"] == "packet_zip"
