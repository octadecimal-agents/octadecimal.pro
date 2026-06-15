import json
import logging

from mcp.server.fastmcp import FastMCP

from secure_agentic_ai.infrastructure.macos.calendar_provider import list_today_calendar_events
from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig
from secure_agentic_ai.infrastructure.workspace.read_services import (
    list_board_tasks,
    search_wiki,
    wiki_results_payload,
)
from secure_agentic_ai.infrastructure.workspace.read_services import (
    review_pending_summary as fetch_review_pending_summary,
)
from secure_agentic_ai.infrastructure.workspace.state import (
    get_documents_indexed,
    get_llm_active_mode,
    get_llm_fallback_reason,
    get_llm_label,
    get_rag_backend_label,
    get_workspace_status,
    init_workspace_state,
    knowledge_root_exists,
)

logger = logging.getLogger(__name__)


def create_workspace_mcp_server() -> FastMCP:
    # Read-only MCP surface — no write/HITL tools (see workspace_policy.py).
    server = FastMCP("octa-workspace")

    @server.tool(
        name="list_today_calendar",
        description="List today's calendar events from macOS EventKit (calctl) with cache/fixture fallback.",
    )
    async def list_today_calendar() -> str:
        config = WorkspaceConfig.from_env()
        events, source = await list_today_calendar_events(config)
        payload = {
            "source": source,
            "count": len(events),
            "events": [
                {
                    "time": event.time,
                    "title": event.title,
                    "calendar": event.calendar,
                }
                for event in events
            ],
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)

    @server.tool(
        name="workspace_health",
        description="Octa Workspace health: RAG index, LLM mode, calendar source, review queue count.",
    )
    async def workspace_health() -> str:
        await init_workspace_state()
        config = WorkspaceConfig.from_env()
        events, calendar_source = await list_today_calendar_events(config)
        status, issues = get_workspace_status()
        summary = await fetch_review_pending_summary()
        payload = {
            "status": status,
            "documents_indexed": get_documents_indexed(),
            "rag_backend": get_rag_backend_label(),
            "llm_provider": get_llm_label(),
            "llm_active": get_llm_active_mode(),
            "llm_fallback_reason": get_llm_fallback_reason(),
            "calendar_provider": config.calendar_provider,
            "calendar_source": calendar_source,
            "calendar_events_count": len(events),
            "knowledge_root_exists": knowledge_root_exists(config),
            "review_pending_count": summary["count"],
            "issues": issues,
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)

    @server.tool(
        name="wiki_search",
        description="Search Knowledge (hybrid RAG). Returns top sources and excerpts.",
    )
    async def wiki_search(query: str, k: int = 5) -> str:
        results = await search_wiki(query, k=k)
        payload = {"query": query, "results": wiki_results_payload(results)}
        return json.dumps(payload, ensure_ascii=False, indent=2)

    @server.tool(
        name="board_list_tasks",
        description="List workspace board tasks. Optional status filter: todo, doing, blocked, done.",
    )
    async def board_list_tasks(status: str | None = None) -> str:
        tasks = await list_board_tasks(status=status or None)
        payload = {"status": status, "count": len(tasks), "tasks": tasks}
        return json.dumps(payload, ensure_ascii=False, indent=2)

    @server.tool(
        name="review_pending_summary",
        description="HITL review queue summary: pending count and top 3 approval titles (read-only).",
    )
    async def review_pending_summary() -> str:
        payload = await fetch_review_pending_summary()
        return json.dumps(payload, ensure_ascii=False, indent=2)

    return server
