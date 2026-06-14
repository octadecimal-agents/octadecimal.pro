from datetime import UTC, date, datetime
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from secure_agentic_ai.adapters.api.dependencies import get_db_session
from secure_agentic_ai.adapters.workspace.schemas import (
    ApprovalSummary,
    CalendarEvent,
    ChatRequest,
    ChatResponse,
    HealthWorkspaceResponse,
    PlanItemResponse,
    PlanReplaceRequest,
    RetroRequest,
    RetroResponse,
    RetroTodayResponse,
    TaskCreateRequest,
    TaskResponse,
    TaskUpdateRequest,
    WikiSearchResponse,
)
from secure_agentic_ai.application.planning_service import DEFAULT_CALENDAR, generate_daily_plan
from secure_agentic_ai.application.workspace_agent import WorkspaceAgent
from secure_agentic_ai.domain.audit import AuditEvent, AuditEventType
from secure_agentic_ai.infrastructure.persistence.approval_repository import (
    SqlAlchemyApprovalRequestRepository,
    SqlAlchemyAuditWriter,
)
from secure_agentic_ai.infrastructure.workspace.ledger import Task
from secure_agentic_ai.infrastructure.workspace.state import (
    get_config,
    get_documents_indexed,
    get_hybrid_search,
    get_ledger,
    get_rag_backend_label,
    init_workspace_state,
)

router = APIRouter(prefix="/workspace", tags=["workspace"])


async def ensure_workspace_ready() -> None:
    await init_workspace_state()


def _task_response(task: Task) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        team=task.team,
        status=task.status,
        title=task.title,
        intent=task.intent,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.get("/health", response_model=HealthWorkspaceResponse)
async def workspace_health() -> HealthWorkspaceResponse:
    await ensure_workspace_ready()
    config = get_config()
    return HealthWorkspaceResponse(
        status="ok",
        knowledge_root=str(config.knowledge_root),
        ledger_path=str(config.ledger_path),
        documents_indexed=get_documents_indexed(),
        rag_backend=get_rag_backend_label(),
    )


@router.post("/chat", response_model=ChatResponse)
async def workspace_chat(body: ChatRequest) -> ChatResponse:
    await ensure_workspace_ready()
    agent = WorkspaceAgent(ledger=get_ledger(), search=get_hybrid_search())
    reply = await agent.chat(body.message, active_hash=body.active_hash)
    return ChatResponse(
        message=reply.message,
        suggested_hash=reply.suggested_hash,
        citations=list(reply.citations),
    )


@router.get("/board/tasks", response_model=list[TaskResponse])
async def list_board_tasks(team: str | None = None, status: str | None = None) -> list[TaskResponse]:
    await ensure_workspace_ready()
    tasks = get_ledger().list_tasks(team=team, status=status)
    return [_task_response(t) for t in tasks]


@router.post("/board/tasks", response_model=TaskResponse)
async def create_board_task(body: TaskCreateRequest) -> TaskResponse:
    await ensure_workspace_ready()
    try:
        task = get_ledger().create_task(
            team=body.team,
            title=body.title,
            intent=body.intent,
            status=body.status,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _task_response(task)


@router.patch("/board/tasks/{task_id}", response_model=TaskResponse)
async def update_board_task(task_id: str, body: TaskUpdateRequest) -> TaskResponse:
    await ensure_workspace_ready()
    try:
        task = get_ledger().update_task_status(task_id, body.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return _task_response(task)


@router.get("/planning/items", response_model=list[PlanItemResponse])
async def list_plan_items(plan_date: str | None = None) -> list[PlanItemResponse]:
    await ensure_workspace_ready()
    day = plan_date or date.today().isoformat()
    items = get_ledger().list_plan_items(day)
    return [
        PlanItemResponse(
            id=item.id,
            plan_date=item.plan_date,
            sort_order=item.sort_order,
            title=item.title,
            source=item.source,
        )
        for item in items
    ]


@router.put("/planning/items", response_model=list[PlanItemResponse])
async def replace_plan_items(body: PlanReplaceRequest) -> list[PlanItemResponse]:
    await ensure_workspace_ready()
    rows = [(item.title, item.source) for item in body.items]
    items = get_ledger().replace_plan_items(body.plan_date, rows)
    return [
        PlanItemResponse(
            id=item.id,
            plan_date=item.plan_date,
            sort_order=item.sort_order,
            title=item.title,
            source=item.source,
        )
        for item in items
    ]


@router.post("/planning/generate", response_model=list[PlanItemResponse])
async def generate_plan(plan_date: str | None = None) -> list[PlanItemResponse]:
    await ensure_workspace_ready()
    day = plan_date or date.today().isoformat()
    items = generate_daily_plan(get_ledger(), plan_date=day)
    return [
        PlanItemResponse(
            id=item.id,
            plan_date=item.plan_date,
            sort_order=item.sort_order,
            title=item.title,
            source=item.source,
        )
        for item in items
    ]


@router.get("/planning/calendar", response_model=list[CalendarEvent])
async def planning_calendar_stub() -> list[CalendarEvent]:
    return [CalendarEvent(time=time, title=title) for time, title in DEFAULT_CALENDAR]


@router.get("/wiki/search", response_model=WikiSearchResponse)
async def wiki_search(q: str, k: int = 5) -> WikiSearchResponse:
    await ensure_workspace_ready()
    results = await get_hybrid_search().search(q, k=k)
    payload: list[dict[str, str | float]] = [
        {
            "source": r.chunk.metadata.source if r.chunk.metadata else "",
            "excerpt": r.chunk.text[:240],
            "score": round(float(r.score), 4),
        }
        for r in results
    ]
    return WikiSearchResponse(query=q, results=payload)


@router.get("/review/pending", response_model=list[ApprovalSummary])
async def review_pending(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[ApprovalSummary]:
    repo = SqlAlchemyApprovalRequestRepository(session)
    pending = await repo.list_pending()
    return [
        ApprovalSummary(
            request_id=req.request_id,
            description=req.action.description,
            actor_display_name=req.requested_by.display_name,
            risk_level=req.action.risk_level.value,
            action_type=req.action.action_type.value,
        )
        for req in pending
    ]


@router.post("/review/{request_id}/approve")
async def review_approve(
    request_id: str,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, str]:
    repo = SqlAlchemyApprovalRequestRepository(session)
    req = await repo.find_by_id(request_id)
    if req is None:
        raise HTTPException(status_code=404, detail="Approval request not found")
    approved = req.approve()
    await repo.update_status(request_id, approved.status.value, approved.decided_at)
    writer = SqlAlchemyAuditWriter(session)
    await writer.record(
        AuditEvent(
            event_id=str(uuid4()),
            event_type=AuditEventType.APPROVAL_APPROVED,
            actor_id="ceo-workspace",
            action_type=approved.action.action_type.value,
            request_id=request_id,
        )
    )
    return {"status": "approved", "request_id": request_id}


@router.post("/review/{request_id}/reject")
async def review_reject(
    request_id: str,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, str]:
    repo = SqlAlchemyApprovalRequestRepository(session)
    req = await repo.find_by_id(request_id)
    if req is None:
        raise HTTPException(status_code=404, detail="Approval request not found")
    rejected = req.reject()
    await repo.update_status(request_id, rejected.status.value, rejected.decided_at)
    writer = SqlAlchemyAuditWriter(session)
    await writer.record(
        AuditEvent(
            event_id=str(uuid4()),
            event_type=AuditEventType.APPROVAL_REJECTED,
            actor_id="ceo-workspace",
            action_type=rejected.action.action_type.value,
            request_id=request_id,
        )
    )
    return {"status": "rejected", "request_id": request_id}


@router.get("/retro/today", response_model=RetroTodayResponse)
async def retro_today() -> RetroTodayResponse:
    await ensure_workspace_ready()
    config = get_config()
    config.journal_dir.mkdir(parents=True, exist_ok=True)
    path = config.journal_dir / f"{date.today().isoformat()}.md"
    content = path.read_text(encoding="utf-8") if path.is_file() else None
    return RetroTodayResponse(path=str(path), content=content)


@router.post("/retro", response_model=RetroResponse)
async def save_retro(body: RetroRequest) -> RetroResponse:
    await ensure_workspace_ready()
    config = get_config()
    config.journal_dir.mkdir(parents=True, exist_ok=True)
    path = config.journal_dir / f"{date.today().isoformat()}.md"
    stamp = datetime.now(UTC).strftime("%H:%M UTC")
    content = (
        f"# Retro — {date.today().isoformat()}\n\n"
        f"_Updated {stamp}_\n\n"
        f"## Co poszło dobrze\n\n{body.went_well.strip()}\n\n"
        f"## Co poprawić\n\n{body.improve.strip()}\n\n"
        f"## Jutro\n\n{body.tomorrow.strip()}\n"
    )
    path.write_text(content, encoding="utf-8")
    return RetroResponse(path=str(path), content=content)
