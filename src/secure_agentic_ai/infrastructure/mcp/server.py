from mcp.server.fastmcp import FastMCP

from secure_agentic_ai.application.use_cases import RequestActionUseCase
from secure_agentic_ai.infrastructure.mcp.tool_handler import MCPToolHandler


def create_mcp_server(use_case: RequestActionUseCase) -> FastMCP:
    handler = MCPToolHandler(use_case)
    server = FastMCP("secure-agentic-ai")

    @server.tool(
        name="read_document",
        description="Read a governance document by its identifier. "
        "Available documents: governance-overview, policy-rules, audit-trail",
    )
    async def read_document(document_id: str) -> str:
        return await handler.read_document(document_id)

    return server
