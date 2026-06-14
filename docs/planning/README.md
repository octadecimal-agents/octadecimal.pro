<link rel="stylesheet" href="../styles/main.css">

# Planowanie projektu

Prywatny indeks planów dla projektu **Secure Agentic AI Platform**.

Ten katalog służy do prowadzenia roadmapy, instrukcji faz, decyzji roboczych i notatek pomagających przejść z doświadczenia PHP/backend do roli AI Engineer w trybie code-first Python.

---

## Główna nawigacja

- [Roadmapa robocza](roadmap-draft.md) — pełna prywatna mapa faz projektu.
- [Konwencje planowania](planning-conventions.md) — jak pisać prywatne plany, w tym sekcje `Referencje do PHP`.
- [Faza 1: Python Platform Foundation](phase-1-python-foundation.md) — tooling, pakiet, testy, CI.
- [Faza 2: Domain Model For Governance](phase-2-domain-governance.md) — czysta domena: actor, action, approval, policy.
- [Faza 3: Application Layer And Governance Use Cases](phase-3-application-use-cases.md) — use case'y, command objects, porty, `Protocol`.
- [Faza 4: FastAPI Async Application Boundary](phase-4-fastapi-async-boundary.md) — cienki HTTP adapter nad application.
- [Faza 5: Async Persistence And Audit Trail](phase-5-async-persistence-audit.md) — PostgreSQL, SQLAlchemy async, audit.
- [Faza 6: LangGraph HITL Workflow And Agent Memory](phase-6-langgraph-hitl-memory.md) — graph, interrupt/resume, checkpointing.
- [Faza 7: RAG Foundation](phase-7-rag-foundation.md) — ingestion, embeddings, retriever, vector store.
- [Faza 8: AI Security And Prompt Injection](phase-8-ai-security-prompt-injection.md) — prompt injection, guardrails, negative tests.
- [Faza 9: Observability, Evals And Cost Monitoring](phase-9-observability-evals-costs.md) — traces, evals, token/cost metrics.
- [Faza 10: MCP Integration And External Tool Context](phase-10-mcp-tool-context.md) — MCP, tool exposure, policy boundary.
- [Faza 11: Secret Manager Integration](phase-11-secret-manager.md) — SecretProvider, Bitwarden, audit.
- [Faza 12: Minimal Operator Demo](phase-12-minimal-operator-demo.md) — operator console, approval demo.
- [Faza 13: Portfolio Polish](phase-13-portfolio-polish.md) — README, diagrams, demo script, ADR-y.
- [Octa Workspace MVP — plan dalszych prac](workspace-mvp-roadmap.md) — fazy M5.1–M5.5 po lokalnym MVP.
  - **Zamknięte:** [indeks Sprint 0–3](workspace-mvp-done-index.md) · [S0](workspace-mvp-sprint-0-boot.md) · [S1](workspace-mvp-sprint-1-chat-wiki.md) · [S2](workspace-mvp-sprint-2-panels-hitl.md) · [S3](workspace-mvp-sprint-3-retro-infra.md) · [rozszerzenia](workspace-mvp-done-extensions.md)
  - **Otwarte:** [M5.1](workspace-mvp-m5-1-hardening.md) · [M5.2](workspace-mvp-m5-2-rag-scale.md) · [M5.3](workspace-mvp-m5-3-ao-evals.md) · [M5.4](workspace-mvp-m5-4-macos-mcp.md) · [M5.5](workspace-mvp-m5-5-prod-bridge.md) · [M6+](workspace-mvp-m6-platform.md)

---

## Status faz

| Faza | Status | Plik | Główny efekt |
| --- | --- | --- | --- |
| 0 | zamknięta roboczo | [Roadmapa](roadmap-draft.md#faza-0-strategic-baseline) | strategia i zatrzymanie dryfu |
| 1 | zakończona | [phase-1-python-foundation.md](phase-1-python-foundation.md) | profesjonalny fundament Python |
| 2 | zakończona | [phase-2-domain-governance.md](phase-2-domain-governance.md) | model governance w czystym Pythonie |
| 3 | zakończona | [phase-3-application-use-cases.md](phase-3-application-use-cases.md) | application layer bez frameworków |
| 4 | w toku | [phase-4-fastapi-async-boundary.md](phase-4-fastapi-async-boundary.md) | FastAPI async boundary |
| 5 | draft | [phase-5-async-persistence-audit.md](phase-5-async-persistence-audit.md) | persistence i audit trail |
| 6 | draft | [phase-6-langgraph-hitl-memory.md](phase-6-langgraph-hitl-memory.md) | LangGraph HITL i memory |
| 7 | draft | [phase-7-rag-foundation.md](phase-7-rag-foundation.md) | RAG foundation |
| 8 | draft | [phase-8-ai-security-prompt-injection.md](phase-8-ai-security-prompt-injection.md) | AI security |
| 9 | draft | [phase-9-observability-evals-costs.md](phase-9-observability-evals-costs.md) | observability, evals, koszty |
| 10 | draft | [phase-10-mcp-tool-context.md](phase-10-mcp-tool-context.md) | MCP/tool context |
| 11 | draft | [phase-11-secret-manager.md](phase-11-secret-manager.md) | secret manager |
| 12 | draft | [phase-12-minimal-operator-demo.md](phase-12-minimal-operator-demo.md) | minimal demo |
| 13 | draft | [phase-13-portfolio-polish.md](phase-13-portfolio-polish.md) | portfolio polish |

---

## Ścieżka czytania

Jeśli wracasz po przerwie:

1. Przeczytaj [Roadmapę roboczą](roadmap-draft.md#decyzje-po-korekcie-roadmapy).
2. Sprawdź aktualną fazę w tabeli powyżej.
3. Otwórz plan aktualnej fazy.
4. Przy niejasnych pojęciach przejdź do sekcji [Powiązane technologie](#powiazane-technologie).
5. Jeśli temat ma dobre przełożenie z PHP, sprawdź sekcję `Referencje do PHP` w pliku fazy.

---

## Powiązane technologie

### Fundament Python

- [Python](../technologies/Python.md)
- [PHP → Python](../technologies/PHP-do-Python.md)
- [uv](../technologies/uv.md)
- [Ruff](../technologies/Ruff.md)
- [Mypy](../technologies/Mypy.md)
- [Pytest](../technologies/Pytest.md)
- [GitHub Actions](../technologies/GitHubActions.md)

### Architektura

- [Clean Architecture](../technologies/CleanArchitecture.md)
- [DDD](../technologies/DDD.md)
- [RBAC](../technologies/RBAC.md)
- [HITL](../technologies/HITL.md)
- [Agentyczny paradygmat](../technologies/AgentycznyParadygmat.md)

### API i backend

- [FastAPI](../technologies/FastAPI.md)
- [Pydantic](../technologies/Pydantic.md)
- [SQLAlchemy](../technologies/SQLAlchemy.md)
- [Alembic](../technologies/Alembic.md)
- [PostgreSQL](../technologies/PostgreSQL.md)
- [Docker](../technologies/Docker.md)

### Agentic AI

- [LLM](../technologies/LLM.md)
- [Tool Use](../technologies/ToolUse.md)
- [LangChain](../technologies/LangChain.md)
- [LangGraph](../technologies/LangGraph.md)
- [Agent Memory](../technologies/AgentMemory.md)
- [MCP](../technologies/MCP.md)

### RAG

- [RAG](../technologies/RAG.md)
- [Embeddings](../technologies/Embeddings.md)
- [Qdrant](../technologies/Qdrant.md)
- [pgvector](../technologies/pgvector.md)

### Security, observability, evals

- [Prompt Injection](../technologies/PromptInjection.md)
- [Guardrails](../technologies/Guardrails.md)
- [Bitwarden Secrets Manager](../technologies/BitwardenSecretsManager.md)
- [Langfuse](../technologies/Langfuse.md)
- [OpenTelemetry](../technologies/OpenTelemetry.md)
- [LLM Evals](../technologies/LLMEvals.md)
- [Promptfoo](../technologies/Promptfoo.md)
- [Grafana](../technologies/Grafana.md)

---

## Powiązane pytania rekrutacyjne

- [Python Developer — pytania](../questions/python-developer/README.md)
- [AI Engineer / LLM Engineer — pytania](../questions/ai-engineer-llm-agents/README.md)

Najważniejsze na obecnym etapie:

- [PY-M06: Dataclasses i typing](../questions/python-developer/PY-M06-dataclasses-typing.md)
- [PY-M09: Typowanie i mypy](../questions/python-developer/PY-M09-typowanie-mypy.md)
- [PY-M10: Testowanie pytest](../questions/python-developer/PY-M10-testowanie-pytest.md)
- [Q12: Agent vs chain](../questions/ai-engineer-llm-agents/Q12-agent-vs-chain.md)
- [Q32: HITL](../questions/ai-engineer-llm-agents/Q32-hitl-implementacja.md)

---

## Mapa faz do technologii

```text
Faza 1:
  Python -> uv -> Ruff -> Mypy -> Pytest -> GitHub Actions

Faza 2:
  Clean Architecture -> DDD -> HITL -> RBAC

Faza 3:
  Clean Architecture -> Protocol/typing -> Pytest fakes -> PHP-to-Python

Faza 4:
  FastAPI -> Pydantic -> async -> httpx/TestClient

Faza 5:
  SQLAlchemy -> Alembic -> PostgreSQL -> Docker

Faza 6:
  LangGraph -> AgentMemory -> HITL

Faza 7:
  RAG -> Embeddings -> Qdrant / pgvector

Faza 8:
  PromptInjection -> Guardrails -> Promptfoo

Faza 9:
  Langfuse -> OpenTelemetry -> LLMEvals -> cost monitoring

Faza 10:
  MCP -> ToolUse -> security boundary

Faza 11:
  BitwardenSecretsManager -> SecretProvider pattern
```

---

## Zasada pracy

Najpierw rozumiemy fazę prywatnie, potem implementujemy mały publiczny slice.

```text
prywatne wyjaśnienie -> mały plan -> kod -> testy -> review -> commit
```

Nie każdy prywatny plan musi trafić do repo publicznego. Publiczne repo ma pokazywać jakość procesu, nie cały proces myślenia.
