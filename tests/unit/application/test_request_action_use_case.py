from secure_agentic_ai.application.commands import RequestActionCommand
from secure_agentic_ai.application.use_cases import (
    RequestActionResult,
    RequestActionStatus,
    RequestActionUseCase,
)
from secure_agentic_ai.domain.actors import Actor, ActorType
from secure_agentic_ai.domain.approvals import ApprovalRequest
from secure_agentic_ai.domain.policies import Action, ActionType, PolicyDecision, RiskLevel


class FakeApprovalRequestRepository:
    def __init__(self) -> None:
        self.saved: list[ApprovalRequest] = []

    def save(self, request: ApprovalRequest) -> None:
        self.saved.append(request)


class FakeAuditWriter:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def record(self, message: str) -> None:
        self.messages.append(message)


def test_human_low_risk_action_is_allowed_without_approval() -> None:
    repository = FakeApprovalRequestRepository()
    audit_writer = FakeAuditWriter()
    use_case = RequestActionUseCase(
        request_repository=repository,
        audit_writer=audit_writer,
    )
    command = RequestActionCommand(
        request_id="req-001",
        actor=Actor(
            actor_id="human-001",
            actor_type=ActorType.HUMAN,
            display_name="Human Reviewer",
        ),
        action=Action(
            action_type=ActionType.CREATE_CONTENT,
            risk_level=RiskLevel.LOW,
            description="Create documentation draft",
        ),
    )

    result = use_case.execute(command)

    assert result == RequestActionResult(
        status=RequestActionStatus.ALLOWED,
        evaluation=result.evaluation,
    )
    assert result.evaluation.decision is PolicyDecision.ALLOW
    assert result.approval_request is None
    assert repository.saved == []
    assert audit_writer.messages == [
        "Action content.create allowed for human-001",
    ]


def test_agent_high_risk_action_creates_approval_request() -> None:
    repository = FakeApprovalRequestRepository()
    audit_writer = FakeAuditWriter()
    use_case = RequestActionUseCase(
        request_repository=repository,
        audit_writer=audit_writer,
    )
    command = RequestActionCommand(
        request_id="req-002",
        actor=Actor(
            actor_id="agent-001",
            actor_type=ActorType.AGENT,
            display_name="Developer Agent",
        ),
        action=Action(
            action_type=ActionType.WRITE_FILE,
            risk_level=RiskLevel.HIGH,
            description="Write generated source file",
        ),
    )

    result = use_case.execute(command)

    assert result.status is RequestActionStatus.APPROVAL_REQUIRED
    assert result.evaluation.decision is PolicyDecision.REQUIRE_APPROVAL
    assert result.approval_request is not None
    assert result.approval_request.request_id == "req-002"
    assert result.approval_request.action == command.action
    assert result.approval_request.requested_by == command.actor
    assert repository.saved == [result.approval_request]
    assert audit_writer.messages == [
        "Approval required for action file.write by agent-001",
    ]


def test_agent_secret_resolution_is_denied_without_approval_request() -> None:
    repository = FakeApprovalRequestRepository()
    audit_writer = FakeAuditWriter()
    use_case = RequestActionUseCase(
        request_repository=repository,
        audit_writer=audit_writer,
    )
    command = RequestActionCommand(
        request_id="req-003",
        actor=Actor(
            actor_id="agent-001",
            actor_type=ActorType.AGENT,
            display_name="Developer Agent",
        ),
        action=Action(
            action_type=ActionType.RESOLVE_SECRET,
            risk_level=RiskLevel.HIGH,
            description="Resolve provider token",
        ),
    )

    result = use_case.execute(command)

    assert result.status is RequestActionStatus.DENIED
    assert result.evaluation.decision is PolicyDecision.DENY
    assert result.approval_request is None
    assert repository.saved == []
    assert audit_writer.messages == [
        "Action secret.resolve denied for agent-001",
    ]
