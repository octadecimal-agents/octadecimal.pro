from typing import Protocol

from secure_agentic_ai.domain.approvals import ApprovalRequest


class ApprovalRequestRepository(Protocol):
    def save(self, request: ApprovalRequest) -> None: ...


class AuditWriter(Protocol):
    def record(self, message: str) -> None: ...
