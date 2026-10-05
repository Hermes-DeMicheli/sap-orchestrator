"""Input validation helpers — 2026 best practice: validate early, fail fast."""

import re
from typing import Any

MAX_NAME_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 1000
MAX_STEPS_PER_WORKFLOW = 50
MAX_PAYLOAD_SIZE_BYTES = 100_000  # 100 KB
VALID_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


class ValidationError(ValueError):
    """Raised when input validation fails."""

    pass


def validate_workflow_name(name: str) -> None:
    if not name or len(name) > MAX_NAME_LENGTH:
        raise ValidationError(f"Name must be 1-{MAX_NAME_LENGTH} chars")


def validate_step_id(step_id: str) -> None:
    if not VALID_ID_RE.match(step_id):
        raise ValidationError(f"Step id must match {VALID_ID_RE.pattern}")


def validate_payload(payload: dict) -> None:
    size = len(str(payload).encode("utf-8"))
    if size > MAX_PAYLOAD_SIZE_BYTES:
        raise ValidationError(f"Payload exceeds {MAX_PAYLOAD_SIZE_BYTES} bytes")


def validate_workflow(steps: list[dict[str, Any]], name: str) -> None:
    validate_workflow_name(name)
    if not steps:
        raise ValidationError("Workflow must have at least one step")
    if len(steps) > MAX_STEPS_PER_WORKFLOW:
        raise ValidationError(f"Max {MAX_STEPS_PER_WORKFLOW} steps per workflow")
    for s in steps:
        validate_step_id(s.get("id", ""))
        validate_payload(s.get("payload", {}))
