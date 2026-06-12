<link rel="stylesheet" href=".dev/styles/main.css">

# Secure Agentic AI Platform

**Secure governance** and **observability** platform for agentic AI workflows with **RAG**, **HITL** approvals, **LLM evals** and **audit trails**.

## Status

Early architecture and implementation phase.

## Goal

Build a **portfolio-grade agentic AI platform** that demonstrates **secure multi-step AI workflows**, **human-in-the-loop approval gates**, **observability**, **evaluation-driven development**, and **audit-ready architecture**.

## Planned Stack

- Python 3.12/3.13
- FastAPI
- Pydantic v2
- LangGraph
- LangChain
- Qdrant
- PostgreSQL + pgvector
- Langfuse
- OpenTelemetry
- Docker
- GitHub Actions
- Playwright

## Core Capabilities

- RAG workflows
- HITL approval gates
- LLM evaluation pipeline
- Self-correcting agent loops
- Prompt injection checks
- Audit trails
- Observability and tracing

## Development

This project uses Python 3.13 and `uv` for dependency and environment management.

Install dependencies:

```bash
uv sync
```

Run local quality checks:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy .
```

## License

MIT
