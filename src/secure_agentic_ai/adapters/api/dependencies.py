from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from secure_agentic_ai.application.ports import ApprovalRequestRepository, AuditWriter
from secure_agentic_ai.application.use_cases import RequestActionUseCase
from secure_agentic_ai.infrastructure.persistence.approval_repository import (
    SqlAlchemyApprovalRequestRepository,
    SqlAlchemyAuditWriter,
)
from secure_agentic_ai.infrastructure.persistence.session import (
    create_engine,
    create_session_factory,
)

_engine: AsyncEngine | None = None
_session_factory = None


def init_db() -> None:
    global _engine, _session_factory
    _engine = create_engine()
    _session_factory = create_session_factory(_engine)


async def shutdown_db() -> None:
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_approval_request_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ApprovalRequestRepository:
    return SqlAlchemyApprovalRequestRepository(session)


async def get_audit_writer(
    session: AsyncSession = Depends(get_db_session),
) -> AuditWriter:
    return SqlAlchemyAuditWriter(session)


async def get_request_action_use_case(
    repository: ApprovalRequestRepository = Depends(get_approval_request_repository),
    audit_writer: AuditWriter = Depends(get_audit_writer),
) -> RequestActionUseCase:
    return RequestActionUseCase(request_repository=repository, audit_writer=audit_writer)
