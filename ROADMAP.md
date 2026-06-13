# Roadmap

## Implemented

| Phase | Focus | Key Outputs |
|-------|-------|-------------|
| 1 | Python foundation | `pyproject.toml`, uv, ruff, mypy, pytest |
| 2 | Domain governance | Actor, Action, Policy, ApprovalRequest, AuditEvent |
| 3 | Application layer | RequestActionUseCase, Protocol ports, fake adapters |
| 4 | FastAPI boundary | `/health`, `/actions` endpoints, Pydantic schemas, DI |
| 5 | Async persistence | SQLAlchemy async, Alembic, approval + audit tables |
| 6 | LangGraph HITL | Policy_check → human_review → execute, interrupt/resume |
| 7 | RAG | Chunking, embeddings, similarity search, ingest + retrieve |
| 8 | AI security | Prompt injection detection (direct + indirect), safety integration |
| 9 | Observability | Tracing, cost estimation, eval runner with synthetic datasets |
| 10 | MCP | FastMCP server, policy-governed read_document tool |
| 11 | Secrets | SecretProvider port, Fake/Env/Bitwarden adapters, masked values |
| 12 | Operator demo | Jinja2 operator console: approvals, audit, approve/reject |
| 13 | Portfolio polish | README, architecture docs, threat model, CI, ADRs |

## Planned

- **Langfuse / OpenTelemetry** — replace DebugTracer with production tracing
- **MCP tool registry** — dynamic tool registration with risk-level metadata
- **Eval CI** — run eval datasets automatically in GitHub Actions
- **Docker Compose** — PostgreSQL deployment profile
- **Playwright e2e** — operator console interaction tests
- **pgvector adapter** — replace InMemoryVectorStore with PostgreSQL vector search
