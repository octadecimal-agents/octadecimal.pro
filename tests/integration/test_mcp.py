import anyio
import pytest
from mcp import types
from mcp.client.session import ClientSession
from mcp.server.fastmcp import FastMCP

from secure_agentic_ai.application.use_cases import (
    RequestActionStatus,
    RequestActionUseCase,
)
from secure_agentic_ai.domain.policies import PolicyDecision, PolicyEvaluation
from secure_agentic_ai.infrastructure.mcp.server import create_mcp_server
from secure_agentic_ai.infrastructure.mcp.tool_handler import MCPToolHandler, ToolExecutionError


class FakeApprovalRequestRepository:
    def __init__(self) -> None:
        self.saved = []

    async def save(self, request) -> None:
        self.saved.append(request)


class FakeAuditWriter:
    def __init__(self) -> None:
        self.events = []

    async def record(self, event) -> None:
        self.events.append(event)


@pytest.fixture
def use_case():
    return RequestActionUseCase(
        request_repository=FakeApprovalRequestRepository(),
        audit_writer=FakeAuditWriter(),
    )


@pytest.mark.asyncio
async def test_handler_reads_document_when_allowed(use_case):
    handler = MCPToolHandler(use_case)
    content = await handler.read_document("governance-overview")
    assert "governance" in content
    assert "autonomous agents" in content


@pytest.mark.asyncio
async def test_handler_raises_on_unknown_document(use_case):
    handler = MCPToolHandler(use_case)
    with pytest.raises(ToolExecutionError, match="Document not found"):
        await handler.read_document("nonexistent-doc")


@pytest.mark.asyncio
async def test_handler_denied_when_use_case_denies():
    class DenyUseCase:
        async def execute(self, command):
            return type(
                "Result",
                (),
                {
                    "status": RequestActionStatus.DENIED,
                    "evaluation": PolicyEvaluation(
                        decision=PolicyDecision.DENY,
                        reason="Agents cannot resolve secrets",
                    ),
                },
            )()

    handler = MCPToolHandler(DenyUseCase())
    with pytest.raises(ToolExecutionError, match="Tool execution denied"):
        await handler.read_document("governance-overview")


@pytest.mark.asyncio
async def test_handler_reads_policy_rules_document(use_case):
    handler = MCPToolHandler(use_case)
    content = await handler.read_document("policy-rules")
    assert "Policy evaluation" in content


@pytest.mark.asyncio
async def test_handler_reads_audit_trail_document(use_case):
    handler = MCPToolHandler(use_case)
    content = await handler.read_document("audit-trail")
    assert "audit trail" in content


@pytest.mark.asyncio
async def test_handler_records_audit_event(use_case):
    handler = MCPToolHandler(use_case)
    await handler.read_document("governance-overview")
    assert len(use_case.audit_writer.events) >= 1
    event = use_case.audit_writer.events[0]
    assert event.event_type.value == "action.allowed"
    assert event.action_type == "context.read"


def _make_mcp_server(use_case: RequestActionUseCase) -> FastMCP:
    return create_mcp_server(use_case)


@pytest.mark.asyncio
async def test_mcp_server_list_tools(use_case):
    server = _make_mcp_server(use_case)

    client_write, server_read = anyio.create_memory_object_stream(0)
    server_write, client_read = anyio.create_memory_object_stream(0)

    async def run_server():
        await server._mcp_server.run(
            server_read,
            server_write,
            server._mcp_server.create_initialization_options(),
        )

    async with anyio.create_task_group() as tg:
        tg.start_soon(run_server)

        async with ClientSession(client_read, client_write) as session:
            await session.initialize()
            result = await session.list_tools()
            names = [t.name for t in result.tools]
            assert "read_document" in names

        tg.cancel_scope.cancel()


@pytest.mark.asyncio
async def test_mcp_server_call_tool_allowed(use_case):
    server = _make_mcp_server(use_case)

    client_write, server_read = anyio.create_memory_object_stream(0)
    server_write, client_read = anyio.create_memory_object_stream(0)

    async def run_server():
        await server._mcp_server.run(
            server_read,
            server_write,
            server._mcp_server.create_initialization_options(),
        )

    async with anyio.create_task_group() as tg:
        tg.start_soon(run_server)

        async with ClientSession(client_read, client_write) as session:
            await session.initialize()
            result = await session.call_tool(
                "read_document",
                {"document_id": "governance-overview"},
            )
            assert result.content
            text = "".join(c.text for c in result.content if isinstance(c, types.TextContent))
            assert "governance" in text

        tg.cancel_scope.cancel()


@pytest.mark.asyncio
async def test_mcp_server_call_tool_returns_error_for_unknown_doc(use_case):
    server = _make_mcp_server(use_case)

    client_write, server_read = anyio.create_memory_object_stream(0)
    server_write, client_read = anyio.create_memory_object_stream(0)

    async def run_server():
        await server._mcp_server.run(
            server_read,
            server_write,
            server._mcp_server.create_initialization_options(),
        )

    async with anyio.create_task_group() as tg:
        tg.start_soon(run_server)

        async with ClientSession(client_read, client_write) as session:
            await session.initialize()
            result = await session.call_tool(
                "read_document",
                {"document_id": "nonexistent"},
            )
            assert result.isError
            text = "".join(c.text for c in result.content if isinstance(c, types.TextContent))
            assert "not found" in text

        tg.cancel_scope.cancel()
