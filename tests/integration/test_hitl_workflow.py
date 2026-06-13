import pytest
from langgraph.types import Command

from secure_agentic_ai.application.commands import RequestActionCommand
from secure_agentic_ai.application.use_cases import RequestActionUseCase
from secure_agentic_ai.domain.actors import Actor, ActorType
from secure_agentic_ai.domain.policies import Action, ActionType, RiskLevel
from secure_agentic_ai.infrastructure.workflows.hitl_workflow import (
    HITLWorkflowState,
    build_hitl_workflow,
)


class FakeApprovalRequestRepository:
    def __init__(self) -> None:
        self.saved = []

    async def save(self, request) -> None:
        self.saved.append(request)


class FakeAuditWriter:
    def __init__(self) -> None:
        self.events = []

    async def record(self, event) -> None:
        self.events.append(event)


@pytest.fixture
def use_case():
    return RequestActionUseCase(
        request_repository=FakeApprovalRequestRepository(),
        audit_writer=FakeAuditWriter(),
    )


@pytest.mark.asyncio
async def test_allows_low_risk_human_action(use_case):
    graph = build_hitl_workflow(use_case)

    command = RequestActionCommand(
        request_id="req-001",
        actor=Actor(actor_id="human-001", actor_type=ActorType.HUMAN, display_name="Human"),
        action=Action(
            action_type=ActionType.READ_CONTEXT,
            risk_level=RiskLevel.LOW,
            description="Read context",
        ),
    )

    result = await graph.ainvoke(
        HITLWorkflowState(command=command, policy_result=None, approval_decision=None),
        {"configurable": {"thread_id": "test-allow"}},
    )

    assert result["policy_result"] is not None
    assert result["policy_result"].status.value == "allowed"


@pytest.mark.asyncio
async def test_denies_agent_secret_resolution(use_case):
    graph = build_hitl_workflow(use_case)

    command = RequestActionCommand(
        request_id="req-002",
        actor=Actor(actor_id="agent-001", actor_type=ActorType.AGENT, display_name="Agent"),
        action=Action(
            action_type=ActionType.RESOLVE_SECRET,
            risk_level=RiskLevel.HIGH,
            description="Resolve secret",
        ),
    )

    result = await graph.ainvoke(
        HITLWorkflowState(command=command, policy_result=None, approval_decision=None),
        {"configurable": {"thread_id": "test-deny"}},
    )

    assert result["policy_result"] is not None
    assert result["policy_result"].status.value == "denied"


@pytest.mark.asyncio
async def test_pauses_for_human_approval(use_case):
    graph = build_hitl_workflow(use_case)

    command = RequestActionCommand(
        request_id="req-003",
        actor=Actor(actor_id="agent-001", actor_type=ActorType.AGENT, display_name="Agent"),
        action=Action(
            action_type=ActionType.WRITE_FILE,
            risk_level=RiskLevel.HIGH,
            description="Write file",
        ),
    )

    config = {"configurable": {"thread_id": "test-hitl"}}
    result = await graph.ainvoke(
        HITLWorkflowState(command=command, policy_result=None, approval_decision=None),
        config,
    )

    assert result["policy_result"] is not None
    assert result["policy_result"].status.value == "approval_required"
    assert "__interrupt__" in result
    assert len(result["__interrupt__"]) > 0

    snapshot = await graph.aget_state(config)
    assert snapshot.next == ("human_review",)


@pytest.mark.asyncio
async def test_resumes_after_human_approval(use_case):
    graph = build_hitl_workflow(use_case)

    command = RequestActionCommand(
        request_id="req-004",
        actor=Actor(actor_id="agent-001", actor_type=ActorType.AGENT, display_name="Agent"),
        action=Action(
            action_type=ActionType.WRITE_FILE,
            risk_level=RiskLevel.HIGH,
            description="Write file",
        ),
    )

    config = {"configurable": {"thread_id": "test-resume-approve"}}
    await graph.ainvoke(
        HITLWorkflowState(command=command, policy_result=None, approval_decision=None),
        config,
    )

    result = await graph.ainvoke(Command(resume="approved"), config)

    assert result["approval_decision"] == "approved"
    assert result["policy_result"] is not None
    assert result["policy_result"].status.value == "approval_required"


@pytest.mark.asyncio
async def test_resumes_after_human_rejection(use_case):
    graph = build_hitl_workflow(use_case)

    command = RequestActionCommand(
        request_id="req-005",
        actor=Actor(actor_id="agent-001", actor_type=ActorType.AGENT, display_name="Agent"),
        action=Action(
            action_type=ActionType.WRITE_FILE,
            risk_level=RiskLevel.HIGH,
            description="Write file",
        ),
    )

    config = {"configurable": {"thread_id": "test-resume-reject"}}
    await graph.ainvoke(
        HITLWorkflowState(command=command, policy_result=None, approval_decision=None),
        config,
    )

    result = await graph.ainvoke(Command(resume="rejected"), config)

    assert result["approval_decision"] == "rejected"
    assert result["policy_result"] is not None
    assert result["policy_result"].status.value == "approval_required"
