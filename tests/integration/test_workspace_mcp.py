import anyio
import pytest
from mcp.client.session import ClientSession

from secure_agentic_ai.infrastructure.mcp.workspace_server import create_workspace_mcp_server


@pytest.mark.asyncio
async def test_workspace_mcp_lists_calendar_tool(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CALENDAR_PROVIDER", "fixture")
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
            tools = await session.list_tools()
            names = {tool.name for tool in tools.tools}
            assert "list_today_calendar" in names
            assert "workspace_health" in names

            result = await session.call_tool("list_today_calendar", {})
            text = "".join(part.text for part in result.content if hasattr(part, "text"))
            assert "events" in text
            assert "source" in text

        tg.cancel_scope.cancel()
