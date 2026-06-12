from secure_agentic_ai.application.ports import ApprovalRequestRepository, AuditWriter
from secure_agentic_ai.application.use_cases import RequestActionUseCase
from secure_agentic_ai.domain.approvals import ApprovalRequest


class InMemoryApprovalRequestRepository:
    def __init__(self) -> None:
        self.saved: list[ApprovalRequest] = []

    def save(self, request: ApprovalRequest) -> None:
        self.saved.append(request)


class InMemoryAuditWriter:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def record(self, message: str) -> None:
        self.messages.append(message)


_request_repository: ApprovalRequestRepository = InMemoryApprovalRequestRepository()
_audit_writer: AuditWriter = InMemoryAuditWriter()


def get_request_action_use_case() -> RequestActionUseCase:
    return RequestActionUseCase(
        request_repository=_request_repository,
        audit_writer=_audit_writer,
    )
