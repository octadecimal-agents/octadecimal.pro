import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from secure_agentic_ai.application.commands import RequestActionCommand
from secure_agentic_ai.application.use_cases import RequestActionUseCase
from secure_agentic_ai.domain.actors import Actor, ActorType
from secure_agentic_ai.domain.approvals import ApprovalRequest, ApprovalStatus
from secure_agentic_ai.domain.audit import AuditEventType
from secure_agentic_ai.domain.policies import Action, ActionType, RiskLevel
from secure_agentic_ai.infrastructure.persistence.approval_repository import (
    SqlAlchemyApprovalRequestRepository,
    SqlAlchemyAuditWriter,
)
from secure_agentic_ai.infrastructure.persistence.models import (
    AuditEventRow,
    Base,
)


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


async def count_audit_events(session: AsyncSession) -> int:
    result = await session.execute(select(AuditEventRow))
    return len(result.scalars().all())


async def get_audit_event_types(session: AsyncSession) -> list[str]:
    result = await session.execute(select(AuditEventRow.event_type))
    return [row[0] for row in result.all()]


@pytest_asyncio.fixture
async def approval_repository(db_session):
    return SqlAlchemyApprovalRequestRepository(db_session)


@pytest_asyncio.fixture
async def audit_writer(db_session):
    return SqlAlchemyAuditWriter(db_session)


@pytest_asyncio.fixture
async def use_case(approval_repository, audit_writer):
    return RequestActionUseCase(
        request_repository=approval_repository,
        audit_writer=audit_writer,
    )


@pytest.mark.asyncio
async def test_allows_low_risk_human_action(use_case, db_session):
    command = RequestActionCommand(
        request_id="req-001",
        actor=Actor(actor_id="human-001", actor_type=ActorType.HUMAN, display_name="Human Operator"),
        action=Action(
            action_type=ActionType.READ_CONTEXT,
            risk_level=RiskLevel.LOW,
            description="Read system context",
        ),
    )

    result = await use_case.execute(command)

    assert result.status.value == "allowed"
    assert await count_audit_events(db_session) == 1
    event_types = await get_audit_event_types(db_session)
    assert event_types == [AuditEventType.ACTION_ALLOWED.value]


@pytest.mark.asyncio
async def test_requires_approval_for_high_risk_agent_action(use_case, approval_repository, db_session):
    command = RequestActionCommand(
        request_id="req-002",
        actor=Actor(actor_id="agent-001", actor_type=ActorType.AGENT, display_name="Dev Agent"),
        action=Action(
            action_type=ActionType.WRITE_FILE,
            risk_level=RiskLevel.HIGH,
            description="Write generated source file",
        ),
    )

    result = await use_case.execute(command)

    assert result.status.value == "approval_required"
    assert result.approval_request is not None
    assert result.approval_request.status.value == "pending"
    assert await count_audit_events(db_session) == 1
    event_types = await get_audit_event_types(db_session)
    assert event_types == [AuditEventType.APPROVAL_REQUESTED.value]

    saved = await approval_repository.find_by_id("req-002")
    assert saved is not None
    assert saved.status.value == "pending"


@pytest.mark.asyncio
async def test_denies_agent_secret_resolution(use_case, db_session):
    command = RequestActionCommand(
        request_id="req-003",
        actor=Actor(actor_id="agent-001", actor_type=ActorType.AGENT, display_name="Dev Agent"),
        action=Action(
            action_type=ActionType.RESOLVE_SECRET,
            risk_level=RiskLevel.HIGH,
            description="Resolve API key",
        ),
    )

    result = await use_case.execute(command)

    assert result.status.value == "denied"
    assert await count_audit_events(db_session) == 1
    event_types = await get_audit_event_types(db_session)
    assert event_types == [AuditEventType.ACTION_DENIED.value]


@pytest.mark.asyncio
async def test_updates_approval_request_status(approval_repository):
    from secure_agentic_ai.domain.actors import Actor
    from secure_agentic_ai.domain.policies import Action

    request = ApprovalRequest(
        request_id="req-004",
        action=Action(
            action_type=ActionType.RUN_COMMAND,
            risk_level=RiskLevel.HIGH,
            description="Run system command",
        ),
        requested_by=Actor(
            actor_id="agent-001",
            actor_type=ActorType.AGENT,
            display_name="Dev Agent",
        ),
    )

    await approval_repository.save(request)
    saved = await approval_repository.find_by_id("req-004")
    assert saved is not None
    assert saved.status == ApprovalStatus.PENDING

    approved = saved.approve()
    await approval_repository.update_status(
        request_id="req-004",
        status=approved.status.value,
        decided_at=approved.decided_at,
    )

    updated = await approval_repository.find_by_id("req-004")
    assert updated is not None
    assert updated.status == ApprovalStatus.APPROVED
    assert updated.decided_at is not None
