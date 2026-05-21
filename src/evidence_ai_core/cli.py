from __future__ import annotations

import argparse
import json
from pathlib import Path
from .packet import create_static_packet
from .verify import verify_packet

def main(argv=None) -> int:
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

    inspect = sub.add_parser("inspect")
    inspect.add_argument("packet_dir")

    args = parser.parse_args(argv)

    if args.command == "create-static":
        request_text = args.request_text
        if args.request_file:
            request_text = Path(args.request_file).read_text(encoding="utf-8")
        packet_dir = create_static_packet(request_text=request_text, source_paths=args.source, output_root=args.output_root)
        print(packet_dir)
        return 0

    if args.command in {"verify", "inspect"}:
        result = verify_packet(args.packet_dir)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["verification_status"] == "passed_mechanical_checks" else 1

    return 2

if __name__ == "__main__":
    raise SystemExit(main())
