from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from .errors import EvidenceCoreError
from .export import export_packet_zip
from .import_extract import extract_packet_zip
from .import_preview import preview_packet_zip
from .inspect import inspect_packet
from .inventory import export_packet_inventory_jsonl, inventory_packet_bundle
from .manifest import read_artifact_manifest, summarize_artifact_hashes
from .packet import create_static_packet
from .schema_index import list_schema_contracts, load_schema_contract
from .summary import summarize_packet
from .verify import verify_packet
from .tracelab_bundle import preview_tracelab_bundle


EXIT_OK = 0
EXIT_VERIFICATION_FAILED = 1
EXIT_USAGE_ERROR = 2


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else EXIT_USAGE_ERROR
        return code

    if args.command == "create-static":
        return _create_static(args)

    if args.command == "verify":
        return _verify(args)

    if args.command == "inspect":
        return _inspect(args)

    if args.command == "summary":
        return _summary(args)

    if args.command == "manifest":
        return _manifest(args)

    if args.command == "hash-summary":
        return _hash_summary(args)

    if args.command == "export-zip":
        return _export_zip(args)

    if args.command == "import-zip-preview":
        return _import_zip_preview(args)

    if args.command == "import-zip-extract":
        return _import_zip_extract(args)

    if args.command == "bundle-inventory":
        return _bundle_inventory(args)

    if args.command == "bundle-inventory-jsonl":
        return _bundle_inventory_jsonl(args)

    if args.command == "schema-index":
        return _schema_index(args)

    if args.command == "schema-contract":
        return _schema_contract(args)
        
    if args.command == "tracelab-bundle-preview":
        result = preview_tracelab_bundle(args.bundle_zip)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["preview_status"] == "passed_tracelab_bundle_preview" else 1

    print("error: unknown command", file=sys.stderr)
    return EXIT_USAGE_ERROR


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="evidence-ai-core")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create-static")
    group = create.add_mutually_exclusive_group(required=True)
    group.add_argument("--request-text")
    group.add_argument("--request-file")
    create.add_argument("--source", action="append", required=True)
    create.add_argument("--output-root", default="evidence_packets")

    verify = sub.add_parser("verify")
    verify.add_argument("packet_dir")
    _add_json_output_options(verify)

    inspect = sub.add_parser("inspect")
    inspect.add_argument("packet_dir")
    _add_json_output_options(inspect)

    summary = sub.add_parser("summary")
    summary.add_argument("packet_dir")
    _add_json_output_options(summary)

    manifest = sub.add_parser("manifest")
    manifest.add_argument("packet_dir")
    _add_json_output_options(manifest)

    hash_summary = sub.add_parser("hash-summary")
    hash_summary.add_argument("packet_dir")
    _add_json_output_options(hash_summary)

    export_zip = sub.add_parser("export-zip")
    export_zip.add_argument("packet_dir")
    export_zip.add_argument("--output-zip", required=True)
    export_zip.add_argument("--overwrite", action="store_true")
    _add_json_output_options(export_zip)

    import_preview = sub.add_parser("import-zip-preview")
    import_preview.add_argument("zip_path")
    _add_json_output_options(import_preview)

    import_extract = sub.add_parser("import-zip-extract")
    import_extract.add_argument("zip_path")
    import_extract.add_argument("--output-root", required=True)
    import_extract.add_argument("--overwrite", action="store_true")
    _add_json_output_options(import_extract)

    bundle_inventory = sub.add_parser("bundle-inventory")
    bundle_inventory.add_argument("root")
    bundle_inventory.add_argument("--recursive", action="store_true")
    bundle_inventory.add_argument("--no-zips", action="store_true")
    bundle_inventory.add_argument("--kind", choices=["all", "dirs", "zips"], default="all")
    bundle_inventory.add_argument("--status", choices=["all", "passed", "failed"], default="all")
    bundle_inventory.add_argument(
        "--sort",
        choices=["relative-path", "name", "kind", "verification-status"],
        default="relative-path",
    )
    bundle_inventory.add_argument("--reverse", action="store_true")
    _add_json_output_options(bundle_inventory)

    bundle_inventory_jsonl = sub.add_parser("bundle-inventory-jsonl")
    bundle_inventory_jsonl.add_argument("root")
    bundle_inventory_jsonl.add_argument("--output-jsonl", required=True)
    bundle_inventory_jsonl.add_argument("--recursive", action="store_true")
    bundle_inventory_jsonl.add_argument("--no-zips", action="store_true")
    bundle_inventory_jsonl.add_argument("--kind", choices=["all", "dirs", "zips"], default="all")
    bundle_inventory_jsonl.add_argument("--status", choices=["all", "passed", "failed"], default="all")
    bundle_inventory_jsonl.add_argument(
        "--sort",
        choices=["relative-path", "name", "kind", "verification-status"],
        default="relative-path",
    )
    bundle_inventory_jsonl.add_argument("--reverse", action="store_true")
    bundle_inventory_jsonl.add_argument("--overwrite", action="store_true")
    _add_json_output_options(bundle_inventory_jsonl)

    schema_index = sub.add_parser("schema-index")
    schema_index.add_argument("--schema-dir")
    _add_json_output_options(schema_index)

    schema_contract = sub.add_parser("schema-contract")
    schema_contract.add_argument("artifact_or_schema")
    schema_contract.add_argument("--schema-dir")
    _add_json_output_options(schema_contract)

    tracelab_preview = sub.add_parser("tracelab-bundle-preview")
    tracelab_preview.add_argument("bundle_zip")
    _add_json_output_options(tracelab_preview)

    return parser


def _add_json_output_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="emit indented JSON instead of the default compact single-line JSON",
    )


def _create_static(args: argparse.Namespace) -> int:
    try:
        request_text = _resolve_request_text(args)
        source_paths = _resolve_source_paths(args.source)
        packet_dir = create_static_packet(
            request_text=request_text,
            source_paths=source_paths,
            output_root=args.output_root,
        )
    except (EvidenceCoreError, FileNotFoundError, IsADirectoryError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    print(packet_dir)
    return EXIT_OK


def _verify(args: argparse.Namespace) -> int:
    packet_dir = Path(args.packet_dir)
    if not packet_dir.exists():
        print(f"error: packet directory does not exist: {packet_dir}", file=sys.stderr)
        return EXIT_USAGE_ERROR
    if not packet_dir.is_dir():
        print(f"error: packet path is not a directory: {packet_dir}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    result = verify_packet(packet_dir)
    _print_json(result, pretty=args.pretty)
    return (
        EXIT_OK
        if result["verification_status"] == "passed_mechanical_checks"
        else EXIT_VERIFICATION_FAILED
    )


def _inspect(args: argparse.Namespace) -> int:
    packet_dir = Path(args.packet_dir)
    if not packet_dir.exists():
        print(f"error: packet directory does not exist: {packet_dir}", file=sys.stderr)
        return EXIT_USAGE_ERROR
    if not packet_dir.is_dir():
        print(f"error: packet path is not a directory: {packet_dir}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    result = inspect_packet(packet_dir)
    _print_json(result, pretty=args.pretty)
    return (
        EXIT_OK
        if result["verification_status"] == "passed_mechanical_checks"
        else EXIT_VERIFICATION_FAILED
    )



def _summary(args: argparse.Namespace) -> int:
    packet_dir = Path(args.packet_dir)
    if not packet_dir.exists():
        print(f"error: packet directory does not exist: {packet_dir}", file=sys.stderr)
        return EXIT_USAGE_ERROR
    if not packet_dir.is_dir():
        print(f"error: packet path is not a directory: {packet_dir}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    try:
        result = summarize_packet(packet_dir)
    except EvidenceCoreError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    _print_json(result, pretty=args.pretty)
    return (
        EXIT_OK
        if result["verification_status"] == "passed_mechanical_checks"
        else EXIT_VERIFICATION_FAILED
    )


def _manifest(args: argparse.Namespace) -> int:
    packet_dir = Path(args.packet_dir)
    if not packet_dir.exists():
        print(f"error: packet directory does not exist: {packet_dir}", file=sys.stderr)
        return EXIT_USAGE_ERROR
    if not packet_dir.is_dir():
        print(f"error: packet path is not a directory: {packet_dir}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    try:
        result = read_artifact_manifest(packet_dir)
    except EvidenceCoreError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    _print_json(result, pretty=args.pretty)
    return EXIT_OK


def _hash_summary(args: argparse.Namespace) -> int:
    packet_dir = Path(args.packet_dir)
    if not packet_dir.exists():
        print(f"error: packet directory does not exist: {packet_dir}", file=sys.stderr)
        return EXIT_USAGE_ERROR
    if not packet_dir.is_dir():
        print(f"error: packet path is not a directory: {packet_dir}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    try:
        result = summarize_artifact_hashes(packet_dir)
    except EvidenceCoreError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    _print_json(result, pretty=args.pretty)
    return (
        EXIT_OK
        if result["verification_status"] == "passed_mechanical_checks"
        else EXIT_VERIFICATION_FAILED
    )




def _export_zip(args: argparse.Namespace) -> int:
    try:
        result = export_packet_zip(
            args.packet_dir,
            args.output_zip,
            overwrite=args.overwrite,
        )
    except EvidenceCoreError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    _print_json(result, pretty=args.pretty)
    return (
        EXIT_OK
        if result["verification_status"] == "passed_mechanical_checks"
        else EXIT_VERIFICATION_FAILED
    )


def _import_zip_preview(args: argparse.Namespace) -> int:
    try:
        result = preview_packet_zip(args.zip_path)
    except EvidenceCoreError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    _print_json(result, pretty=args.pretty)
    return (
        EXIT_OK
        if result["verification_status"] == "passed_mechanical_checks"
        else EXIT_VERIFICATION_FAILED
    )


def _import_zip_extract(args: argparse.Namespace) -> int:
    try:
        result = extract_packet_zip(
            args.zip_path,
            args.output_root,
            overwrite=args.overwrite,
        )
    except EvidenceCoreError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    _print_json(result, pretty=args.pretty)
    return (
        EXIT_OK
        if result["verification_status"] == "passed_mechanical_checks"
        else EXIT_VERIFICATION_FAILED
    )


def _bundle_inventory(args: argparse.Namespace) -> int:
    try:
        result = inventory_packet_bundle(
            args.root,
            recursive=args.recursive,
            include_zips=not args.no_zips,
            kind_filter=args.kind,
            status_filter=args.status,
            sort_by=args.sort,
            reverse=args.reverse,
        )
    except EvidenceCoreError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    _print_json(result, pretty=args.pretty)
    return (
        EXIT_OK
        if result["verification_status"] == "passed_mechanical_checks"
        else EXIT_VERIFICATION_FAILED
    )


def _bundle_inventory_jsonl(args: argparse.Namespace) -> int:
    try:
        result = export_packet_inventory_jsonl(
            args.root,
            args.output_jsonl,
            recursive=args.recursive,
            include_zips=not args.no_zips,
            kind_filter=args.kind,
            status_filter=args.status,
            sort_by=args.sort,
            reverse=args.reverse,
            overwrite=args.overwrite,
        )
    except EvidenceCoreError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    _print_json(result, pretty=args.pretty)
    return (
        EXIT_OK
        if result["verification_status"] == "passed_mechanical_checks"
        else EXIT_VERIFICATION_FAILED
    )


def _schema_index(args: argparse.Namespace) -> int:
    try:
        result = list_schema_contracts(args.schema_dir)
    except EvidenceCoreError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    _print_json(result, pretty=args.pretty)
    return EXIT_OK


def _schema_contract(args: argparse.Namespace) -> int:
    try:
        result = load_schema_contract(args.artifact_or_schema, args.schema_dir)
    except EvidenceCoreError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR

    _print_json(result, pretty=args.pretty)
    return EXIT_OK



def _tracelab_bundle_preview(args: argparse.Namespace) -> int:
    result = preview_tracelab_bundle(args.bundle_zip)
    _print_json(result, pretty=args.pretty)
    return (
        EXIT_OK
        if result["preview_status"] == "passed_tracelab_bundle_preview"
        else EXIT_VERIFICATION_FAILED
    )

def _resolve_request_text(args: argparse.Namespace) -> str:
    if args.request_text is not None:
        return args.request_text

    request_file = Path(args.request_file)
    if not request_file.exists():
        raise FileNotFoundError(f"request file does not exist: {request_file}")
    if not request_file.is_file():
        raise IsADirectoryError(f"request file is not a file: {request_file}")
    return request_file.read_text(encoding="utf-8")


def _resolve_source_paths(source_args: list[str]) -> list[str]:
    source_paths = []
    for source in source_args:
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"source file does not exist: {path}")
        if not path.is_file():
            raise IsADirectoryError(f"source path is not a file: {path}")
        source_paths.append(str(path))
    return source_paths


def _print_json(data: dict[str, Any], *, pretty: bool = False) -> None:
    if pretty:
        print(json.dumps(data, indent=2, sort_keys=True))
        return

    print(json.dumps(data, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    raise SystemExit(main())
