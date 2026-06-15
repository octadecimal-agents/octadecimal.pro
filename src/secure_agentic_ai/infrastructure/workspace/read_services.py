"""Read-only Workspace operations shared by HTTP router and MCP server."""

from __future__ import annotations

from typing import Any

from secure_agentic_ai.adapters.api.dependencies import init_db
from secure_agentic_ai.application.review_queue import PendingReviewItem
from secure_agentic_ai.domain.knowledge import RetrievedChunk
from secure_agentic_ai.infrastructure.persistence.approval_repository import SqlAlchemyApprovalRequestRepository
from secure_agentic_ai.infrastructure.workspace.ledger import Task
from secure_agentic_ai.infrastructure.workspace.review_adapter import pending_review_items
from secure_agentic_ai.infrastructure.workspace.state import get_hybrid_search, get_ledger, init_workspace_state


def task_to_dict(task: Task) -> dict[str, str | None]:
    return {
        "id": task.id,
        "team": task.team,
        "status": task.status,
        "title": task.title,
        "intent": task.intent,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }


async def search_wiki(query: str, k: int = 5) -> list[RetrievedChunk]:
    await init_workspace_state()
    return await get_hybrid_search().search(query, k=k)


def wiki_results_payload(results: list[RetrievedChunk], *, include_debug: bool = False) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    for result in results:
        row: dict[str, Any] = {
            "source": result.chunk.metadata.source if result.chunk.metadata else "",
            "excerpt": result.chunk.text[:240],
            "score": round(float(result.score), 4),
        }
        if include_debug and result.breakdown is not None:
            row["vector_score"] = round(result.breakdown.vector_score, 4)
            row["keyword_score"] = round(result.breakdown.keyword_score, 4)
            row["keyword_raw"] = round(result.breakdown.keyword_raw, 4)
            row["heading_score"] = round(result.breakdown.heading_score, 4)
            row["recency_score"] = round(result.breakdown.recency_score, 4)
        payload.append(row)
    return payload


async def list_board_tasks(status: str | None = None) -> list[dict[str, str | None]]:
    await init_workspace_state()
    return [task_to_dict(task) for task in get_ledger().list_tasks(status=status)]


async def review_pending_summary() -> dict[str, Any]:
    init_db()
    from secure_agentic_ai.adapters.api.dependencies import get_db_session

    pending_items: tuple[PendingReviewItem, ...] = ()
    async for session in get_db_session():
        repo = SqlAlchemyApprovalRequestRepository(session)
        pending_items = pending_review_items(await repo.list_pending())
        break

    top = [
        {
            "request_id": item.request_id,
            "description": item.description,
            "risk_level": item.risk_level,
            "actor_display_name": item.actor_display_name,
        }
        for item in pending_items[:3]
    ]
    return {
        "count": len(pending_items),
        "top": top,
    }
