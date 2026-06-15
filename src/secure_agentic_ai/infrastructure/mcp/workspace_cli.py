from secure_agentic_ai.adapters.api.dependencies import init_db
from secure_agentic_ai.infrastructure.mcp.workspace_server import create_workspace_mcp_server


def main() -> None:
    init_db()
    server = create_workspace_mcp_server()
    server.run()


if __name__ == "__main__":
    main()
