"""EvidenceAI Core: static evidence packet creation, inspection, reading, schema discovery, and verification."""

from .errors import (
    EvidenceCoreError,
    PacketAlreadyExistsError,
    PacketInputError,
    PacketExportError,
    PacketImportError,
    PacketReadError,
    PacketVerificationError,
)
from .export import export_packet_zip
from .import_extract import extract_packet_zip
from .import_preview import preview_packet_zip
from .inspect import inspect_packet
from .inventory import export_packet_inventory_jsonl, inventory_packet_bundle
from .manifest import read_artifact_manifest, summarize_artifact_hashes
from .packet import create_static_packet
from .reader import load_packet
from .schema_index import list_schema_contracts, load_schema_contract
from .summary import summarize_packet
from .verify import verify_packet

from .external_tool_evidence import (
    EXTERNAL_TOOL_EVIDENCE_RECORD_TYPE,
    EXTERNAL_TOOL_EVIDENCE_SCHEMA_VERSION,
    MECHANICAL_STATUS_FAILED,
    MECHANICAL_STATUS_NOT_CHECKED,
    MECHANICAL_STATUS_PASSED,
    MECHANICAL_STATUS_PASSED_WITH_WARNINGS,
    MECHANICAL_STATUS_PREVIEW_ONLY,
    MECHANICAL_STATUS_UNSUPPORTED,
    verify_external_tool_evidence_envelope,
)

__all__ = [
    "EvidenceCoreError",
    "PacketAlreadyExistsError",
    "PacketInputError",
    "PacketExportError",
    "PacketImportError",
    "PacketReadError",
    "PacketVerificationError",
    "create_static_packet",
    "export_packet_zip",
    "extract_packet_zip",
    "export_packet_inventory_jsonl",
    "inspect_packet",
    "inventory_packet_bundle",
    "list_schema_contracts",
    "load_packet",
    "load_schema_contract",
    "preview_packet_zip",
    "read_artifact_manifest",
    "summarize_artifact_hashes",
    "summarize_packet",
    "verify_packet",
    "EXTERNAL_TOOL_EVIDENCE_RECORD_TYPE",
    "EXTERNAL_TOOL_EVIDENCE_SCHEMA_VERSION",
    "MECHANICAL_STATUS_FAILED",
    "MECHANICAL_STATUS_NOT_CHECKED",
    "MECHANICAL_STATUS_PASSED",
    "MECHANICAL_STATUS_PASSED_WITH_WARNINGS",
    "MECHANICAL_STATUS_PREVIEW_ONLY",
    "MECHANICAL_STATUS_UNSUPPORTED",
    "verify_external_tool_evidence_envelope",
]
__version__ = "0.1.0a0"
