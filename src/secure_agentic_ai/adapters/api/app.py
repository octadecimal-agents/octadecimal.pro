from fastapi import FastAPI

from secure_agentic_ai.adapters.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Secure Agentic AI Platform",
        version="0.1.0",
        description="Secure governance boundary for agentic AI workflows.",
    )
    app.include_router(router)
    return app


app = create_app()
