import asyncio
import json
from pathlib import Path

import anyio
import pytest
from mcp.client.session import ClientSession

from secure_agentic_ai.adapters.api.dependencies import init_db
from secure_agentic_ai.infrastructure.mcp.workspace_policy import FORBIDDEN_WRITE_TOOL_NAMES, READ_ONLY_TOOL_NAMES
from secure_agentic_ai.infrastructure.mcp.workspace_server import create_workspace_mcp_server
from secure_agentic_ai.infrastructure.persistence.models import Base
from secure_agentic_ai.infrastructure.persistence.session import create_engine


@pytest.fixture
def mcp_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    knowledge = tmp_path / "knowledge" / "01-Base-Point/pro/servers/pc-ubuntu"
    knowledge.mkdir(parents=True)
    (knowledge / "Backup.md").write_text(
        "# Backup\n\nAutomatyczny backup stacku HYDRA Qdrant retention na pc-ubuntu dev environment.",
        encoding="utf-8",
    )
    db_url = f"sqlite+aiosqlite:///{tmp_path / 'approvals.db'}"
    monkeypatch.setenv("WORKSPACE_ENABLED", "1")
    monkeypatch.setenv("KNOWLEDGE_ROOT", str(tmp_path / "knowledge"))
    monkeypatch.setenv("OCTA_LEDGER", str(tmp_path / "ledger.sqlite"))
    monkeypatch.setenv("LLM_PROVIDER", "dry")
    monkeypatch.setenv("RAG_BACKEND", "memory")
    monkeypatch.setenv("CALENDAR_PROVIDER", "fixture")
    monkeypatch.setenv("DATABASE_URL", db_url)

    async def _create_schema() -> None:
        engine = create_engine(db_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()

    asyncio.run(_create_schema())
    init_db()


async def _with_mcp_session(callback):
    server = create_workspace_mcp_server()
    client_write, server_read = anyio.create_memory_object_stream(0)
    server_write, client_read = anyio.create_memory_object_stream(0)

    async def run_server() -> None:
        await server._mcp_server.run(
            server_read,
            server_write,
            server._mcp_server.create_initialization_options(),
        )

    async with anyio.create_task_group() as tg:
        tg.start_soon(run_server)
        async with ClientSession(client_read, client_write) as session:
            await session.initialize()
            await callback(session)
        tg.cancel_scope.cancel()


@pytest.mark.asyncio
async def test_workspace_mcp_lists_read_only_tools(mcp_env: None) -> None:
    async def check(session: ClientSession) -> None:
        tools = await session.list_tools()
        names = {tool.name for tool in tools.tools}
        assert names == READ_ONLY_TOOL_NAMES
        assert names & FORBIDDEN_WRITE_TOOL_NAMES == set()

    await _with_mcp_session(check)


@pytest.mark.asyncio
async def test_workspace_mcp_calendar_and_health_smoke(mcp_env: None) -> None:
    async def check(session: ClientSession) -> None:
        calendar = await session.call_tool("list_today_calendar", {})
        calendar_text = "".join(part.text for part in calendar.content if hasattr(part, "text"))
        assert "events" in calendar_text
        assert "source" in calendar_text

        health = await session.call_tool("workspace_health", {})
        health_text = "".join(part.text for part in health.content if hasattr(part, "text"))
        health_data = json.loads(health_text)
        assert "calendar_events_count" in health_data
        assert "documents_indexed" in health_data

    await _with_mcp_session(check)


@pytest.mark.asyncio
async def test_workspace_mcp_wiki_and_board_smoke(mcp_env: None) -> None:
    async def check(session: ClientSession) -> None:
        wiki = await session.call_tool("wiki_search", {"query": "backup Qdrant", "k": 3})
        wiki_text = "".join(part.text for part in wiki.content if hasattr(part, "text"))
        wiki_data = json.loads(wiki_text)
        assert wiki_data["results"]
        assert any("Backup.md" in row["source"] for row in wiki_data["results"])

        board = await session.call_tool("board_list_tasks", {"status": "blocked"})
        board_text = "".join(part.text for part in board.content if hasattr(part, "text"))
        board_data = json.loads(board_text)
        assert board_data["status"] == "blocked"
        assert "tasks" in board_data

        review = await session.call_tool("review_pending_summary", {})
        review_text = "".join(part.text for part in review.content if hasattr(part, "text"))
        review_data = json.loads(review_text)
        assert "count" in review_data
        assert "top" in review_data

    await _with_mcp_session(check)
