class EvidenceCoreError(Exception):
    """Base error for evidence-ai-core."""


class PacketInputError(EvidenceCoreError):
    """Raised when static packet input is missing, invalid, or unsafe."""


class PacketAlreadyExistsError(PacketInputError):
    """Raised when static packet creation would overwrite an existing packet."""


class PacketVerificationError(EvidenceCoreError):
    """Raised when packet verification is configured to fail hard."""


class PacketReadError(EvidenceCoreError):
    """Raised when an evidence packet cannot be read as a static packet."""


class PacketExportError(EvidenceCoreError):
    """Raised when a static packet ZIP export cannot be completed safely."""


class PacketImportError(EvidenceCoreError):
    """Raised when a static packet ZIP import preview cannot be completed safely."""
