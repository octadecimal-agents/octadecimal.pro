import json

from mcp.server.fastmcp import FastMCP

from secure_agentic_ai.infrastructure.macos.calendar_provider import list_today_calendar_events
from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig
from secure_agentic_ai.infrastructure.workspace.state import (
    get_documents_indexed,
    get_llm_label,
    get_rag_backend_label,
    init_workspace_state,
)


def create_workspace_mcp_server() -> FastMCP:
    server = FastMCP("octa-workspace")

    @server.tool(
        name="list_today_calendar",
        description="List today's calendar events from macOS EventKit (calctl) with fixture fallback.",
    )
    async def list_today_calendar() -> str:
        config = WorkspaceConfig.from_env()
        events, source = await list_today_calendar_events(config)
        payload = {
            "source": source,
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
        description="Octa Workspace MVP health: RAG index, LLM provider, calendar provider mode.",
    )
    async def workspace_health() -> str:
        await init_workspace_state()
        config = WorkspaceConfig.from_env()
        payload = {
            "status": "ok",
            "documents_indexed": get_documents_indexed(),
            "rag_backend": get_rag_backend_label(),
            "llm_provider": get_llm_label(),
            "calendar_provider": config.calendar_provider,
        }
        return json.dumps(payload, indent=2)

    return server
