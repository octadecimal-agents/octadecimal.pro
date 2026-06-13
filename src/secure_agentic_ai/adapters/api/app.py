from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from secure_agentic_ai.adapters.api.dependencies import init_db, shutdown_db
from secure_agentic_ai.adapters.api.operator_router import router as operator_router
from secure_agentic_ai.adapters.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    init_db()
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
    return app


app = create_app()
