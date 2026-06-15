from datetime import UTC, datetime
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from secure_agentic_ai.adapters.api.dependencies import get_db_session
from secure_agentic_ai.domain.audit import AuditEvent, AuditEventType
from secure_agentic_ai.infrastructure.persistence.approval_repository import (
    SqlAlchemyApprovalRequestRepository,
    SqlAlchemyAuditReader,
    SqlAlchemyAuditWriter,
)

templates = Jinja2Templates(directory="src/secure_agentic_ai/adapters/api/templates")

router = APIRouter(prefix="/operator")


def _repo(session: AsyncSession) -> SqlAlchemyApprovalRequestRepository:
    return SqlAlchemyApprovalRequestRepository(session)


def _reader(session: AsyncSession) -> SqlAlchemyAuditReader:
    return SqlAlchemyAuditReader(session)


def _writer(session: AsyncSession) -> SqlAlchemyAuditWriter:
    return SqlAlchemyAuditWriter(session)


@router.get("")
async def dashboard(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    repo = _repo(session)
    reader = _reader(session)
    pending = await repo.list_pending()
    recent = await reader.list_recent(limit=100)
    now = datetime.now(UTC)
    recent_24h = [e for e in recent if (now - e.timestamp).total_seconds() < 86400]
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "pending_count": len(pending),
            "audit_count": len(recent_24h),
            "pending": pending,
            "flash": None,
        },
    )


@router.get("/approvals")
async def list_approvals(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    repo = _repo(session)
    pending = await repo.list_pending()
    return templates.TemplateResponse(
        request,
        "approvals.html",
        {"requests": pending},
    )


@router.post("/approvals/{request_id}/approve")
async def approve_request(
    request_id: str,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    repo = _repo(session)
    req = await repo.find_by_id(request_id)
    if req is None:
        return RedirectResponse(url="/operator/approvals", status_code=303)
    approved = req.approve()
    await repo.update_status(request_id, approved.status.value, approved.decided_at)
    writer = _writer(session)
    event = AuditEvent(
        event_id=str(uuid4()),
        event_type=AuditEventType.APPROVAL_APPROVED,
        actor_id="operator",
        action_type=approved.action.action_type.value,
        request_id=request_id,
    )
    await writer.record(event)
    return RedirectResponse(url="/operator/approvals", status_code=303)


@router.post("/approvals/{request_id}/reject")
async def reject_request(
    request_id: str,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    repo = _repo(session)
    req = await repo.find_by_id(request_id)
    if req is None:
        return RedirectResponse(url="/operator/approvals", status_code=303)
    rejected = req.reject()
    await repo.update_status(request_id, rejected.status.value, rejected.decided_at)
    writer = _writer(session)
    event = AuditEvent(
        event_id=str(uuid4()),
        event_type=AuditEventType.APPROVAL_REJECTED,
        actor_id="operator",
        action_type=rejected.action.action_type.value,
        request_id=request_id,
    )
    await writer.record(event)
    return RedirectResponse(url="/operator/approvals", status_code=303)


@router.get("/audit")
async def list_audit(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    reader = _reader(session)
    events = await reader.list_recent(limit=100)
    return templates.TemplateResponse(
        request,
        "audit.html",
        {"events": events},
    )
