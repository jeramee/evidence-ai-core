class EvidenceCoreError(Exception):
    """Base error for evidence-ai-core."""


class PacketVerificationError(EvidenceCoreError):
    """Raised when packet verification is configured to fail hard."""
