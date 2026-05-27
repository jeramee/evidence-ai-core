"""Generic external-tool evidence envelope mechanics.

This module is deliberately local and mechanical. It describes and checks
external-tool evidence records, but it does not execute tools, call models,
run retrieval, validate scientific truth, or promote claims.
"""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any


EXTERNAL_TOOL_EVIDENCE_RECORD_TYPE = "external_tool_evidence_envelope"
EXTERNAL_TOOL_EVIDENCE_SCHEMA_VERSION = "0.1"

MECHANICAL_STATUS_NOT_CHECKED = "not_checked"
MECHANICAL_STATUS_PASSED = "passed"
MECHANICAL_STATUS_PASSED_WITH_WARNINGS = "passed_with_warnings"
MECHANICAL_STATUS_FAILED = "failed"
MECHANICAL_STATUS_PREVIEW_ONLY = "preview_only"
MECHANICAL_STATUS_UNSUPPORTED = "unsupported"

ISSUE_SEVERITY_INFO = "info"
ISSUE_SEVERITY_WARNING = "warning"
ISSUE_SEVERITY_ERROR = "error"

PREFERRED_TOOL_FAMILIES = {
    "txtai",
    "paperetl",
    "rag",
    "txtchat",
    "ncoder",
    "unknown",
}

PREFERRED_TOOL_ROLES = {
    "retrieval_index",
    "source_etl",
    "rag_support",
    "chat_app",
    "coding_agent",
    "workflow_artifact",
    "derived_artifact",
    "unknown",
}

PREFERRED_ARTIFACT_ROLES = {
    "input",
    "config",
    "output",
    "derived",
    "index",
    "preview",
    "report",
    "manifest",
    "log",
    "unknown",
}

REQUIRED_AUTHORITY_LIMITS = {
    "mechanical_integrity_only",
    "no_truth_validation",
    "no_model_authority",
    "no_claim_promotion",
}

OPTIONAL_AUTHORITY_LIMITS = {
    "no_rag_answer_validation",
    "no_external_tool_execution",
    "no_scientific_validity",
}

KNOWN_AUTHORITY_LIMITS = REQUIRED_AUTHORITY_LIMITS | OPTIONAL_AUTHORITY_LIMITS

REQUIRED_ENVELOPE_FIELDS = (
    "record_type",
    "schema_version",
    "trace_id",
    "tool_family",
    "tool_role",
    "artifacts",
    "mechanical_verification_status",
    "authority_limits",
)

REQUIRED_ARTIFACT_FIELDS = (
    "artifact_id",
    "artifact_role",
    "path",
    "required_for_verification",
)


def verify_external_tool_evidence_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    """Verify one external-tool evidence envelope mechanically.

    Verification is limited to shape, required fields, preferred vocabulary
    warnings, safe relative artifact paths, required-hash presence, required
    authority limits, and mechanical status derivation.
    """

    issues: list[dict[str, Any]] = []

    if not isinstance(envelope, dict):
        issues.append(
            _issue(
                "invalid_envelope",
                ISSUE_SEVERITY_ERROR,
                "External tool evidence envelope must be an object.",
            )
        )
        return _result(None, MECHANICAL_STATUS_FAILED, issues)

    for field in REQUIRED_ENVELOPE_FIELDS:
        if field not in envelope:
            issues.append(
                _issue(
                    "required_field_missing",
                    ISSUE_SEVERITY_ERROR,
                    f"Envelope is missing required field: {field}.",
                    field=field,
                )
            )

    record_type = envelope.get("record_type")
    if record_type is not None and record_type != EXTERNAL_TOOL_EVIDENCE_RECORD_TYPE:
        issues.append(
            _issue(
                "invalid_record_type",
                ISSUE_SEVERITY_ERROR,
                "Envelope record_type must be external_tool_evidence_envelope.",
                field="record_type",
            )
        )

    schema_version = envelope.get("schema_version")
    if "schema_version" in envelope:
        if not isinstance(schema_version, str) or not schema_version.strip():
            issues.append(
                _issue(
                    "invalid_schema_version",
                    ISSUE_SEVERITY_ERROR,
                    "Envelope schema_version must be a non-empty string.",
                    field="schema_version",
                )
            )
        elif schema_version != EXTERNAL_TOOL_EVIDENCE_SCHEMA_VERSION:
            issues.append(
                _issue(
                    "unsupported_schema_version",
                    ISSUE_SEVERITY_WARNING,
                    "Envelope schema version is present, but this core version cannot verify it.",
                    field="schema_version",
                )
            )
            return _result(envelope.get("trace_id"), MECHANICAL_STATUS_UNSUPPORTED, issues)

    tool_family = envelope.get("tool_family")
    if isinstance(tool_family, str) and tool_family not in PREFERRED_TOOL_FAMILIES:
        issues.append(
            _issue(
                "unknown_tool_family",
                ISSUE_SEVERITY_WARNING,
                "tool_family is not in the preferred vocabulary.",
                field="tool_family",
            )
        )

    tool_role = envelope.get("tool_role")
    if isinstance(tool_role, str) and tool_role not in PREFERRED_TOOL_ROLES:
        issues.append(
            _issue(
                "unknown_tool_role",
                ISSUE_SEVERITY_WARNING,
                "tool_role is not in the preferred vocabulary.",
                field="tool_role",
            )
        )

    _check_authority_limits(envelope.get("authority_limits"), issues)
    _check_artifacts(envelope.get("artifacts"), issues)

    return _result(envelope.get("trace_id"), _status_from_issues(issues), issues)


def _check_authority_limits(authority_limits: Any, issues: list[dict[str, Any]]) -> None:
    if not isinstance(authority_limits, list):
        issues.append(
            _issue(
                "authority_limits_invalid",
                ISSUE_SEVERITY_ERROR,
                "authority_limits must be a list.",
                field="authority_limits",
            )
        )
        return

    observed = {item for item in authority_limits if isinstance(item, str)}
    missing = sorted(REQUIRED_AUTHORITY_LIMITS - observed)
    for limit in missing:
        issues.append(
            _issue(
                "required_authority_limit_missing",
                ISSUE_SEVERITY_ERROR,
                f"authority_limits is missing required non-claim: {limit}.",
                field="authority_limits",
            )
        )

    for index, item in enumerate(authority_limits):
        if not isinstance(item, str):
            issues.append(
                _issue(
                    "authority_limit_invalid",
                    ISSUE_SEVERITY_ERROR,
                    "authority_limits entries must be strings.",
                    field=f"authority_limits[{index}]",
                )
            )
        elif item not in KNOWN_AUTHORITY_LIMITS:
            issues.append(
                _issue(
                    "unknown_authority_limit",
                    ISSUE_SEVERITY_WARNING,
                    "authority_limits entry is not in the preferred vocabulary.",
                    field=f"authority_limits[{index}]",
                )
            )


def _check_artifacts(artifacts: Any, issues: list[dict[str, Any]]) -> None:
    if not isinstance(artifacts, list):
        issues.append(
            _issue(
                "artifacts_invalid",
                ISSUE_SEVERITY_ERROR,
                "artifacts must be a list.",
                field="artifacts",
            )
        )
        return

    for index, artifact in enumerate(artifacts):
        field_prefix = f"artifacts[{index}]"

        if not isinstance(artifact, dict):
            issues.append(
                _issue(
                    "artifact_invalid",
                    ISSUE_SEVERITY_ERROR,
                    "Artifact entry must be an object.",
                    field=field_prefix,
                )
            )
            continue

        artifact_id = artifact.get("artifact_id")
        artifact_role = artifact.get("artifact_role")
        path = artifact.get("path")
        required_for_verification = artifact.get("required_for_verification")

        for field in REQUIRED_ARTIFACT_FIELDS:
            if field not in artifact:
                issues.append(
                    _issue(
                        "required_artifact_field_missing",
                        ISSUE_SEVERITY_ERROR,
                        f"Artifact is missing required field: {field}.",
                        artifact_id=artifact_id if isinstance(artifact_id, str) else None,
                        field=f"{field_prefix}.{field}",
                    )
                )

        if isinstance(artifact_role, str):
            if artifact_role not in PREFERRED_ARTIFACT_ROLES:
                issues.append(
                    _issue(
                        "unknown_artifact_role",
                        ISSUE_SEVERITY_WARNING,
                        "artifact_role is not in the preferred vocabulary.",
                        artifact_id=artifact_id if isinstance(artifact_id, str) else None,
                        field=f"{field_prefix}.artifact_role",
                    )
                )
            elif artifact_role == "unknown" and required_for_verification is True:
                issues.append(
                    _issue(
                        "unknown_artifact_role_required_for_verification",
                        ISSUE_SEVERITY_WARNING,
                        "artifact_role is unknown but marked required for verification.",
                        artifact_id=artifact_id if isinstance(artifact_id, str) else None,
                        field=f"{field_prefix}.artifact_role",
                    )
                )

        if not isinstance(path, str) or not path.strip():
            issues.append(
                _issue(
                    "artifact_path_invalid",
                    ISSUE_SEVERITY_ERROR,
                    "Artifact path must be a non-empty safe relative path.",
                    artifact_id=artifact_id if isinstance(artifact_id, str) else None,
                    field=f"{field_prefix}.path",
                )
            )
        elif not _is_safe_relative_path(path):
            issues.append(
                _issue(
                    "unsafe_artifact_path",
                    ISSUE_SEVERITY_ERROR,
                    "Artifact path must be packet-local and relative.",
                    artifact_id=artifact_id if isinstance(artifact_id, str) else None,
                    path=path,
                    field=f"{field_prefix}.path",
                )
            )

        if required_for_verification is True:
            sha256 = artifact.get("sha256")
            if not isinstance(sha256, str) or not sha256.strip():
                issues.append(
                    _issue(
                        "required_artifact_hash_missing",
                        ISSUE_SEVERITY_ERROR,
                        "Artifact is required for verification but has no sha256.",
                        artifact_id=artifact_id if isinstance(artifact_id, str) else None,
                        path=path if isinstance(path, str) else None,
                        field=f"{field_prefix}.sha256",
                    )
                )
        elif required_for_verification is False and "sha256" not in artifact:
            issues.append(
                _issue(
                    "optional_artifact_hash_missing",
                    ISSUE_SEVERITY_INFO,
                    "Artifact is not required for verification and has no sha256.",
                    artifact_id=artifact_id if isinstance(artifact_id, str) else None,
                    path=path if isinstance(path, str) else None,
                    field=f"{field_prefix}.sha256",
                )
            )


def _is_safe_relative_path(path: str) -> bool:
    if "\\" in path:
        return False
    if path.startswith("/") or path.startswith("~"):
        return False

    pure_path = PurePosixPath(path)
    if pure_path.is_absolute():
        return False
    if any(part in {"", ".", ".."} for part in pure_path.parts):
        return False
    if len(pure_path.parts) >= 1 and ":" in pure_path.parts[0]:
        return False

    return True


def _status_from_issues(issues: list[dict[str, Any]]) -> str:
    severities = {issue.get("severity") for issue in issues}

    if ISSUE_SEVERITY_ERROR in severities:
        return MECHANICAL_STATUS_FAILED
    if ISSUE_SEVERITY_WARNING in severities:
        return MECHANICAL_STATUS_PASSED_WITH_WARNINGS

    return MECHANICAL_STATUS_PASSED


def _result(trace_id: Any, status: str, issues: list[dict[str, Any]]) -> dict[str, Any]:
    warnings = [issue for issue in issues if issue.get("severity") == ISSUE_SEVERITY_WARNING]
    errors = [issue for issue in issues if issue.get("severity") == ISSUE_SEVERITY_ERROR]

    return {
        "schema_version": EXTERNAL_TOOL_EVIDENCE_SCHEMA_VERSION,
        "record_type": "external_tool_evidence_verification_result",
        "trace_id": trace_id,
        "mechanical_verification_status": status,
        "issue_count": len(issues),
        "warning_count": len(warnings),
        "error_count": len(errors),
        "issues": issues,
        "warnings": warnings,
        "errors": errors,
        "authority_limits": sorted(REQUIRED_AUTHORITY_LIMITS),
        "authority_note": (
            "External tool evidence verification is local mechanical verification only. "
            "It does not execute external tools, validate truth, validate RAG answers, "
            "grant model authority, certify scientific validity, or promote claims."
        ),
    }


def _issue(
    code: str,
    severity: str,
    message: str,
    *,
    artifact_id: str | None = None,
    path: str | None = None,
    field: str | None = None,
) -> dict[str, Any]:
    issue = {
        "code": code,
        "severity": severity,
        "message": message,
    }

    if artifact_id is not None:
        issue["artifact_id"] = artifact_id
    if path is not None:
        issue["path"] = path
    if field is not None:
        issue["field"] = field

    return issue
    