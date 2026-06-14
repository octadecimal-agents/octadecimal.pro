from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from secure_agentic_ai.adapters.api.dependencies import init_db, shutdown_db
from secure_agentic_ai.adapters.api.operator_router import router as operator_router
from secure_agentic_ai.adapters.api.routes import router
from secure_agentic_ai.adapters.workspace.router import router as workspace_router
from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig
from secure_agentic_ai.infrastructure.workspace.state import init_workspace_state

STATIC_DIR = Path(__file__).resolve().parent.parent / "workspace" / "static"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    init_db()
    config = WorkspaceConfig.from_env()
    if config.enabled:
        await init_workspace_state()
    yield
    await shutdown_db()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Secure Agentic AI Platform",
        version="0.1.0",
        description="Secure governance boundary for agentic AI workflows.",
        lifespan=lifespan,
    )
    app.include_router(router)
    app.include_router(operator_router)

    config = WorkspaceConfig.from_env()
    if config.enabled:
        app.include_router(workspace_router)

        @app.get("/", include_in_schema=False)
        async def workspace_index() -> FileResponse:
            return FileResponse(STATIC_DIR / "index.html")

        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="workspace-static")

    return app


app = create_app()
