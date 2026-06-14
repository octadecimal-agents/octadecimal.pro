from dataclasses import dataclass
from datetime import date

from secure_agentic_ai.application.planning_service import generate_daily_plan
from secure_agentic_ai.application.ports import ChatCompletionProvider
from secure_agentic_ai.application.use_cases import RetrieveContextUseCase
from secure_agentic_ai.domain.knowledge import RetrievedChunk
from secure_agentic_ai.infrastructure.llm.deepseek_provider import build_rag_messages, parse_suggested_hash
from secure_agentic_ai.infrastructure.workspace.hybrid_search import HybridKnowledgeSearch
from secure_agentic_ai.infrastructure.workspace.ledger import WorkspaceLedger


@dataclass(frozen=True)
class ChatReply:
    message: str
    suggested_hash: str | None = None
    citations: tuple[str, ...] = ()


class WorkspaceAgent:
    """Personal agent (Maja + Anna persona) for local MVP — dry or DeepSeek-backed."""

    def __init__(
        self,
        ledger: WorkspaceLedger,
        search: HybridKnowledgeSearch | RetrieveContextUseCase,
        chat: ChatCompletionProvider | None = None,
    ) -> None:
        self._ledger = ledger
        self._search_backend = search
        self._chat = chat

    async def chat(self, message: str, active_hash: str | None = None) -> ChatReply:
        lowered = message.lower()

        if any(word in lowered for word in ("zablokow", "blocked", "blokad")):
            blocked = self._ledger.list_tasks(status="blocked")
            if not blocked:
                return ChatReply(
                    message="Nie ma zablokowanych zadań na tablicy. Wszystko płynie — sprawdź `#Board`.",
                    suggested_hash="#Board",
                )
            lines = [f"- **{t.team}**: {t.title}" for t in blocked]
            return ChatReply(
                message="Zablokowane zadania:\n\n" + "\n".join(lines) + "\n\n→ `#Board`",
                suggested_hash="#Board",
            )

        if "wygeneruj plan" in lowered or "generate plan" in lowered:
            items = generate_daily_plan(self._ledger)
            lines = [f"{i + 1}. {item.title}" for i, item in enumerate(items)]
            return ChatReply(
                message="Przygotowałam plan dnia:\n\n" + "\n".join(lines) + "\n\n→ `#Planning`",
                suggested_hash="#Planning",
            )

        if any(word in lowered for word in ("plan", "dzisiaj", "today", "planning")):
            today = date.today().isoformat()
            items = self._ledger.list_plan_items(today)
            if items:
                lines = [f"{i + 1}. {item.title}" for i, item in enumerate(items)]
                body = "Plan na dziś:\n\n" + "\n".join(lines)
            else:
                body = (
                    "Plan na dziś jest pusty. Napisz „wygeneruj plan” albo kliknij "
                    "„Generuj plan” w `#Planning`."
                )
            return ChatReply(message=body + "\n\n→ `#Planning`", suggested_hash="#Planning")

        if any(word in lowered for word in ("review", "akcept", "approve", "hitl")):
            return ChatReply(
                message="Kolejka akceptacji CEO jest w panelu `#Review`. Tam zatwierdzasz akcje wysokiego ryzyka.",
                suggested_hash="#Review",
            )

        citations, chunks = await self._search(message)
        llm_reply = await self._try_llm_reply(message, chunks, citations)
        if llm_reply is not None:
            return llm_reply

        if chunks:
            top = chunks[0]
            excerpt = top.chunk.text[:280].strip()
            if len(top.chunk.text) > 280:
                excerpt += "…"
            source = top.chunk.metadata.source if top.chunk.metadata else "Knowledge"
            reply = f"Znalazłam w Kanonie (**{source}**):\n\n> {excerpt}\n\nPełny kontekst w `#Wiki`."
            if "backup" in lowered or "qdrant" in lowered:
                reply += "\n\n→ `#Wiki` · runbook Operacje/serwer"
            return ChatReply(message=reply, suggested_hash="#Wiki", citations=tuple(citations))

        if active_hash:
            return ChatReply(
                message=f"Jestem tu, w {active_hash}. Zadaj pytanie o Knowledge, plan dnia albo tablicę zadań.",
                suggested_hash=active_hash,
            )

        return ChatReply(
            message=(
                "Dzień dobry! Jestem Agentem Osobistym (Maja + Anna). "
                "Zapytaj o backup, plan dnia albo status zespołów — albo otwórz panel z sidebaru."
            ),
            suggested_hash="#Planning",
        )

    async def _try_llm_reply(
        self,
        message: str,
        chunks: list[RetrievedChunk],
        citations: list[str],
    ) -> ChatReply | None:
        if self._chat is None or not self._chat.is_available():
            return None

        context_blocks: list[tuple[str, str]] = []
        for item in chunks[:5]:
            source = item.chunk.metadata.source if item.chunk.metadata else "Knowledge"
            context_blocks.append((source, item.chunk.text[:1200]))

        try:
            reply_text = await self._chat.complete(build_rag_messages(message, context_blocks))
        except Exception:
            return None

        suggested = parse_suggested_hash(reply_text)
        if suggested is None and chunks:
            suggested = "#Wiki"
        return ChatReply(
            message=reply_text,
            suggested_hash=suggested,
            citations=tuple(citations),
        )

    async def _search(self, query: str) -> tuple[list[str], list[RetrievedChunk]]:
        if isinstance(self._search_backend, HybridKnowledgeSearch):
            chunks = await self._search_backend.search(query, k=5)
        else:
            chunks = await self._search_backend.execute(query, k=5)
        citations: list[str] = []
        for item in chunks:
            source = item.chunk.metadata.source if item.chunk.metadata else ""
            if source and source not in citations:
                citations.append(source)
        return citations, chunks
