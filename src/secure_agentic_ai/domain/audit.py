from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum


class AuditEventType(StrEnum):
    APPROVAL_REQUESTED = "approval.requested"
    APPROVAL_APPROVED = "approval.approved"
    APPROVAL_REJECTED = "approval.rejected"
    ACTION_EXECUTED = "action.executed"
    ACTION_FAILED = "action.failed"
    ACTION_ALLOWED = "action.allowed"
    ACTION_DENIED = "action.denied"


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    event_type: AuditEventType
    actor_id: str
    action_type: str
    request_id: str | None = None
    trace_id: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, str] = field(default_factory=dict)
