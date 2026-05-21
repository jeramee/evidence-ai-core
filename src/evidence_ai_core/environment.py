from __future__ import annotations

from .ids import utc_now_iso
import platform
import sys
import os

def capture_environment(packet_id: str, working_directory: str = ".") -> dict:
    env = {}
    for key in ("PYTHONPATH", "VIRTUAL_ENV"):
        if key in os.environ:
            env[key] = os.environ[key]
    return {
        "schema_version": "0.1",
        "record_type": "environment_report",
        "packet_id": packet_id,
        "environment_id": f"env_{packet_id}",
        "captured_at": utc_now_iso(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "python": {
            "version": sys.version.split()[0],
            "implementation": platform.python_implementation(),
        },
        "packages": [],
        "working_directory": working_directory,
        "environment_variables": env,
        "raw_environment_dumped": False,
        "environment_status": "partial_static_capture",
        "redaction_status": "allowlist_only",
        "warnings": [
            "This environment report supports static packet inspection, not guaranteed replay."
        ],
    }
