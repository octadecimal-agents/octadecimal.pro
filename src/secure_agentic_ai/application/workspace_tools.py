import time
from dataclasses import dataclass
from datetime import date

from secure_agentic_ai.application.review_queue import PendingReviewItem
from secure_agentic_ai.application.use_cases import RetrieveContextUseCase
from secure_agentic_ai.domain.knowledge import RetrievedChunk
from secure_agentic_ai.infrastructure.workspace.hybrid_search import HybridKnowledgeSearch
from secure_agentic_ai.infrastructure.workspace.ledger import Task, WorkspaceLedger


@dataclass(frozen=True)
class ToolResult:
    name: str
    summary: str
    row_count: int
    duration_ms: float


async def knowledge_search(
    search: HybridKnowledgeSearch | RetrieveContextUseCase,
    query: str,
    *,
    k: int = 5,
) -> tuple[ToolResult, list[str], list[RetrievedChunk]]:
    started = time.perf_counter()
    if isinstance(search, HybridKnowledgeSearch):
        chunks = await search.search(query, k=k)
    else:
        chunks = await search.execute(query, k=k)

    citations: list[str] = []
    for item in chunks:
        source = item.chunk.metadata.source if item.chunk.metadata else ""
        if source and source not in citations:
            citations.append(source)

    if not chunks:
        summary = "Brak trafień w Knowledge dla tego zapytania."
    else:
        lines = []
        for item in chunks[:5]:
            source = item.chunk.metadata.source if item.chunk.metadata else "Knowledge"
            excerpt = item.chunk.text[:200].strip()
            if len(item.chunk.text) > 200:
                excerpt += "…"
            lines.append(f"- {source}: {excerpt}")
        summary = "Wyniki Knowledge:\n" + "\n".join(lines)

    duration_ms = round((time.perf_counter() - started) * 1000, 1)
    return (
        ToolResult(
            name="knowledge_search",
            summary=summary,
            row_count=len(chunks),
            duration_ms=duration_ms,
        ),
        citations,
        chunks,
    )


def board_list(ledger: WorkspaceLedger, *, status: str | None = None) -> ToolResult:
    started = time.perf_counter()
    tasks = ledger.list_tasks(status=status)
    if not tasks:
        label = status or "wszystkie"
        summary = f"Tablica ({label}): brak zadań."
    else:
        lines = [_format_task_line(task) for task in tasks[:10]]
        suffix = f"\n… i {len(tasks) - 10} więcej" if len(tasks) > 10 else ""
        summary = f"Tablica ({status or 'wszystkie'}):\n" + "\n".join(lines) + suffix

    duration_ms = round((time.perf_counter() - started) * 1000, 1)
    return ToolResult(
        name="board_list",
        summary=summary,
        row_count=len(tasks),
        duration_ms=duration_ms,
    )


def approvals_pending(pending: tuple[PendingReviewItem, ...]) -> ToolResult:
    started = time.perf_counter()
    if not pending:
        summary = "Kolejka Review: brak akcji do zatwierdzenia."
    else:
        lines = [f"- {item.description} ({item.risk_level}) — {item.actor_display_name}" for item in pending]
        summary = f"Kolejka Review ({len(pending)}):\n" + "\n".join(lines)

    duration_ms = round((time.perf_counter() - started) * 1000, 1)
    return ToolResult(
        name="approvals_pending",
        summary=summary,
        row_count=len(pending),
        duration_ms=duration_ms,
    )


def plan_today(ledger: WorkspaceLedger) -> ToolResult:
    started = time.perf_counter()
    today = date.today().isoformat()
    items = ledger.list_plan_items(today)
    if not items:
        summary = "Plan na dziś: pusty."
    else:
        lines = [f"{index + 1}. {item.title}" for index, item in enumerate(items)]
        summary = "Plan na dziś:\n" + "\n".join(lines)

    duration_ms = round((time.perf_counter() - started) * 1000, 1)
    return ToolResult(
        name="plan_today",
        summary=summary,
        row_count=len(items),
        duration_ms=duration_ms,
    )


def _format_task_line(task: Task) -> str:
    return f"- [{task.status}] {task.team}: {task.title}"
