import pytest

from secure_agentic_ai.application.commands import RequestActionCommand
from secure_agentic_ai.application.use_cases import RequestActionUseCase
from secure_agentic_ai.domain.actors import Actor, ActorType
from secure_agentic_ai.domain.audit import AuditEvent
from secure_agentic_ai.domain.observability import CostEstimate, EvalResult, TokenUsage
from secure_agentic_ai.domain.policies import Action, ActionType, RiskLevel
from secure_agentic_ai.infrastructure.observability.cost_calculator import CostCalculator
from secure_agentic_ai.infrastructure.observability.debug_tracer import DebugTracer
from secure_agentic_ai.infrastructure.observability.eval_dataset import EVAL_CASES
from secure_agentic_ai.infrastructure.observability.eval_runner import EvalRunner
from secure_agentic_ai.infrastructure.security.pattern_safety_checker import PatternSafetyChecker


class FakeApprovalRequestRepository:
    def __init__(self) -> None:
        self.saved = []

    async def save(self, request) -> None:
        self.saved.append(request)


class FakeAuditWriter:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    async def record(self, event: AuditEvent) -> None:
        self.events.append(event)


@pytest.mark.asyncio
async def test_trace_id_in_audit_events():
    tracer = DebugTracer()
    audit = FakeAuditWriter()
    use_case = RequestActionUseCase(
        request_repository=FakeApprovalRequestRepository(),
        audit_writer=audit,
        tracer=tracer,
    )

    command = RequestActionCommand(
        request_id="obs-001",
        actor=Actor(actor_id="human-001", actor_type=ActorType.HUMAN, display_name="Human"),
        action=Action(action_type=ActionType.READ_CONTEXT, risk_level=RiskLevel.LOW, description="Read docs"),
    )

    await use_case.execute(command)

    assert len(audit.events) == 1
    assert audit.events[0].trace_id == tracer.trace_id


@pytest.mark.asyncio
async def test_trace_id_is_none_without_tracer():
    audit = FakeAuditWriter()
    use_case = RequestActionUseCase(
        request_repository=FakeApprovalRequestRepository(),
        audit_writer=audit,
    )

    command = RequestActionCommand(
        request_id="obs-002",
        actor=Actor(actor_id="human-001", actor_type=ActorType.HUMAN, display_name="Human"),
        action=Action(action_type=ActionType.READ_CONTEXT, risk_level=RiskLevel.LOW, description="Read docs"),
    )

    await use_case.execute(command)

    assert audit.events[0].trace_id is None


@pytest.mark.asyncio
async def test_cost_calculator_estimates():
    calc = CostCalculator(model="gpt-4o-mini")

    usage = TokenUsage(input_tokens=500, output_tokens=150)
    estimate = calc.estimate(usage)

    assert isinstance(estimate, CostEstimate)
    assert estimate.total_usd > 0
    assert estimate.model == "gpt-4o-mini"

    expected_input = (500 / 1000) * 0.15
    expected_output = (150 / 1000) * 0.60
    assert estimate.input_cost_usd == round(expected_input, 6)
    assert estimate.output_cost_usd == round(expected_output, 6)
    assert estimate.total_usd == round(expected_input + expected_output, 6)


@pytest.mark.asyncio
async def test_cost_calculator_falls_back_to_default():
    calc = CostCalculator(model="unknown-model")

    usage = TokenUsage(input_tokens=100, output_tokens=100)
    estimate = calc.estimate(usage)

    assert estimate.total_usd > 0
    assert estimate.model == "unknown-model"


@pytest.mark.asyncio
async def test_eval_runner_all_pass():
    repo = FakeApprovalRequestRepository()
    audit = FakeAuditWriter()
    safety = PatternSafetyChecker()
    runner = EvalRunner(repository=repo, audit_writer=audit, safety_checker=safety)

    results = await runner.run(EVAL_CASES)

    assert len(results) == 5
    for r in results:
        assert r.passed, (
            f"Eval '{r.case.name}' failed: expected={r.case.expected_status} got={r.actual_status} error={r.error}"
        )
        assert r.duration_ms >= 0


@pytest.mark.asyncio
async def test_eval_runner_without_safety_checker():
    repo = FakeApprovalRequestRepository()
    audit = FakeAuditWriter()
    runner = EvalRunner(repository=repo, audit_writer=audit)

    results = await runner.run(EVAL_CASES)

    assert len(results) == 5
    for r in results:
        assert isinstance(r, EvalResult)
