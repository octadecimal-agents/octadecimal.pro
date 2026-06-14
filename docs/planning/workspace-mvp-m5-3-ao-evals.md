<link rel="stylesheet" href="../styles/main.css">

# Faza M5.3 — Agent Osobisty (inteligencja + jakość)

[← Workspace MVP roadmap](workspace-mvp-roadmap.md) · [Faza 6 — LangGraph](phase-6-langgraph-hitl-memory.md) · [Faza 9 — evals](phase-9-observability-evals-costs.md)

**Status:** todo · **Szacunek:** 5–10 dni · **Priorytet:** P1 (po M5.2)

## Cel fazy

Agent Osobisty (AO) ma przechodzić z **trybu heurystycznego + RAG** do **kontrolowanego pipeline'u** z mierzalną jakością odpowiedzi. CEO nadal rozmawia po polsku w jednym oknie chat — ale pod spodem wiemy *dlaczego* AO zasugerował `#Wiki` vs `#Review`.

---

## Stan wyjściowy

```text
POST /workspace/chat
        │
        ▼
WorkspaceAgent.chat()
        ├── matches_attention_query → format_attention_reply
        ├── matches_review_query    → format_review_reply
        ├── heurystyki (plan, blocked, …)
        ├── _search() → HybridKnowledgeSearch
        └── _try_llm_reply() → MiniMax / dry
                │
                ▼
        ChatReply { message, suggested_hash, citations }
```

Pliki kluczowe:

- `application/workspace_agent.py` — orchestracja
- `application/review_queue.py` — attention/review copy
- `infrastructure/llm/chat_prompts.py` — RAG messages, sanitize thinking blocks
- `infrastructure/llm/minimax_provider.py` — OpenAI-compatible API

---

## Koncepcja docelowa

### Trzy tryby odpowiedzi (jawnie)

| Tryb | Kiedy | Źródło prawdy |
|------|-------|---------------|
| **Deterministyczny** | attention, review, blocked, plan keywords | `review_queue.py`, ledger |
| **RAG + template** | LLM niedostępny (`dry`) | chunks + heurystyki |
| **RAG + LLM** | MiniMax available | prompt + citations |

AO **nie powinien** halucynować listy approval — to zawsze tryb deterministyczny.

### Structured tools (bez pełnego agentic loop na start)

Zamiast dowolnego function calling od modelu — **agent wywołuje narzędzia w kodzie**, a LLM tylko syntetyzuje odpowiedź z wyników:

```text
User message
    │
    ├── intent router (regex + optional classifier)
    │
    ├── tools (sync/async):
    │     knowledge_search(query)
    │     board_list(status?)
    │     approvals_pending()
    │     plan_today()
    │
    └── LLM synthesize(context_blocks) → ChatReply
```

**Dlaczego nie od razu pełny ReAct?** Mniejsza powierzchnia prompt injection; łatwiejsze testy; zgodne z governance platformy.

### Opcjonalny LangGraph slice (M5.3.3)

Minimalny graf — **spike**, nie produkcja:

```text
[retrieve] → [policy_hint] → [compose_reply] → END
                    │
                    └── interrupt jeśli action wymaga HITL (future)
```

Powiązanie z [Fazą 6](phase-6-langgraph-hitl-memory.md): checkpoint dopiero gdy workflow wielo-krokowy (np. „zaproponuj deploy → czekaj na approve → wykonaj stub”).

---

## Zadania — szczegóły

### M5.3.1 — Persona prompt v2

**Persona:** Maja (struktura, plan) + Anna (ton, ciepło) — krótko, po polsku.

**Plik:** `infrastructure/llm/chat_prompts.py` — `SYSTEM_PROMPT` / `build_rag_messages`.

**Wytyczne promptu:**

1. Zawsze kończ sugestią panelu (`→ #Wiki`) gdy relevant.
2. Cytuj źródło Kanonu ścieżką, nie zmyślonym tytułem.
3. Nie ujawniaj chain-of-thought; `sanitize_llm_reply` usuwa `<think>` / tagi reasoning.
4. Przy braku kontekstu — przyznaj i zaproponuj `#Wiki` search.

**Done when:** review promptów w PR; 3 przykładowe odpowiedzi w docs (anonimizowane).

---

### M5.3.2 — Structured tools

**Implementacja:**

```python
# application/workspace_tools.py (propozycja)
async def knowledge_search(agent, query: str) -> ToolResult: ...
async def board_list(ledger, status: str | None) -> ToolResult: ...
async def approvals_pending(repo) -> ToolResult: ...
async def plan_today(ledger) -> ToolResult: ...
```

`WorkspaceAgent.chat()`:

1. Router decyduje które tools wywołać (np. „co wymaga uwagi” → tylko `approvals_pending`, bez LLM).
2. Wyniki trafiają do `build_rag_messages` jako `context_blocks`.
3. Log dev: `tool_trace: [{name, duration_ms, rows}]`.

**Done when:** log zawiera trace; pytest na router intents.

---

### M5.3.3 — LangGraph slice (opcjonalnie)

**Scope spike (max 2 dni):**

- Jeden plik `infrastructure/workflow/chat_graph.py`
- Stan: `{message, chunks, tool_results, reply}`
- Bez persistence checkpoint — in-memory only
- 1 test integration: message → reply with suggested_hash

**Decyzja po spike:** merge do main **lub** odłożyć do Fazy 6 platformy.

---

### M5.3.4 — Chat eval dataset

**Lokalizacja:** `tests/evals/workspace_chat.yaml`

**Format:**

```yaml
cases:
  - id: attention-pl
    input: "Co wymaga uwagi?"
    expect:
      suggested_hash: "#Review"
      message_contains: ["Review"]
  - id: backup-en-pl
    input: "jak backup Qdrant?"
    expect:
      suggested_hash: "#Wiki"
      message_contains: ["Backup", "Wiki"]
```

**Runner:** `uv run python scripts/run-workspace-evals.py` — używa `LLM_PROVIDER=dry` dla stabilności CI; osobny profil `--live` dla MiniMax manual.

**Done when:** ≥ 10 cases; ≥ 80% pass w dry.

---

### M5.3.5 — RAG eval dataset

**Lokalizacja:** `tests/evals/rag_golden.yaml`

**Runner:** reuse `HybridKnowledgeSearch` + assert top-3 sources.

Powiązane z M5.2.4 — ten sam zestaw golden queries.

---

### M5.3.6 — Fallback chain LLM

**Problem:** brak tokenu MiniMax → cichy fallback do dry myli CEO.

**Rozwiązanie:**

```text
MINIMAX_API_TOKEN missing
    → health.llm_available = false
    → pierwsza wiadomość AO w UI: "Tryb suchy — brak klucza LLM"
    → chat nadal działa (RAG + heurystyki)
```

**Pliki:** `factory.py`, `workspace/health`, `app.js` init message.

**Done when:** health + UI jawnie komunikują tryb.

---

### M5.3.7 — Streaming odpowiedzi (nice-to-have)

**Architektura:**

```text
POST /workspace/chat/stream  → SSE
    event: token
    event: done { suggested_hash, citations }
```

**UI:** append tokenów w `#chat-log`; fallback na JSON POST jeśli SSE unsupported.

**Priorytet:** po M5.3.1–M5.3.6; można odłożyć bez blokowania fazy.

---

## Evals w CI

```text
pytest tests/unit/…           (szybkie, zawsze)
run-workspace-evals.py --dry    (opcjonalny job nightly)
Playwright E2E                  (UX smoke)
```

**Nie** uruchamiać MiniMax w CI (koszt + sekrety).

---

## Bezpieczeństwo (most do Fazy 8)

Już w M5.3:

- Retrieved chunks ≠ instrukcje systemowe (`build_rag_messages` separation).
- `sanitize_llm_reply` — strip thinking leaks.
- Deterministic path dla HITL — model nie „wymyśla” approval count.

Pełny prompt injection suite → [Faza 8](phase-8-ai-security-prompt-injection.md).

---

## Kryterium ukończenia fazy

- [ ] Persona v2 wdrożona
- [ ] Tool trace w dev logs
- [ ] `workspace_chat.yaml` ≥ 80% pass (dry)
- [ ] RAG golden eval PASS
- [ ] Fallback LLM jawny w health/UI
- [ ] pytest + E2E bez regresji

---

## Propozycja commitów

1. `feat(workspace): add structured tool layer for AO`
2. `feat(llm): persona prompt v2 and explicit dry fallback`
3. `test(evals): add workspace chat and RAG golden datasets`
4. `spike(workflow): minimal LangGraph chat slice` (optional)
