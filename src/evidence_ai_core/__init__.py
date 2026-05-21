"""EvidenceAI Core: static evidence packet creation and verification."""

from .packet import create_static_packet
from .verify import verify_packet

__all__ = ["create_static_packet", "verify_packet"]
__version__ = "0.1.0a0"
