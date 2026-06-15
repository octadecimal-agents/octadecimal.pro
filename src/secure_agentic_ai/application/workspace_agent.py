from secure_agentic_ai.application.chat_reply import ChatReply
from secure_agentic_ai.application.planning_service import generate_daily_plan
from secure_agentic_ai.application.ports import ChatCompletionProvider
from secure_agentic_ai.application.review_queue import (
    PendingReviewItem,
    format_attention_reply,
    format_review_reply,
)
from secure_agentic_ai.application.use_cases import RetrieveContextUseCase
from secure_agentic_ai.application.workspace_intent import ChatIntent, classify_chat_intent
from secure_agentic_ai.application.workspace_tool_trace import log_tool_trace
from secure_agentic_ai.application.workspace_tools import (
    ToolResult,
    approvals_pending,
    board_list,
    knowledge_search,
    plan_today,
)
from secure_agentic_ai.domain.knowledge import RetrievedChunk
from secure_agentic_ai.infrastructure.llm.chat_prompts import (
    build_rag_messages,
    parse_suggested_hash,
    sanitize_llm_reply,
)
from secure_agentic_ai.infrastructure.workspace.hybrid_search import HybridKnowledgeSearch
from secure_agentic_ai.infrastructure.workspace.ledger import WorkspaceLedger


class WorkspaceAgent:
    """Personal agent (Maja + Anna persona) for local MVP — dry or external LLM."""

    def __init__(
        self,
        ledger: WorkspaceLedger,
        search: HybridKnowledgeSearch | RetrieveContextUseCase,
        chat: ChatCompletionProvider | None = None,
        pending_reviews: tuple[PendingReviewItem, ...] = (),
    ) -> None:
        self._ledger = ledger
        self._search_backend = search
        self._chat = chat
        self._pending_reviews = pending_reviews

    async def chat(self, message: str, active_hash: str | None = None) -> ChatReply:
        intent = classify_chat_intent(message)
        trace: list[ToolResult] = []

        if intent is ChatIntent.ATTENTION:
            blocked = self._ledger.list_tasks(status="blocked")
            trace.append(approvals_pending(self._pending_reviews))
            trace.append(board_list(self._ledger, status="blocked"))
            log_tool_trace(message, trace)
            return format_attention_reply(
                self._pending_reviews,
                blocked_count=len(blocked),
                blocked_titles=tuple(task.title for task in blocked),
            )

        if intent is ChatIntent.REVIEW:
            trace.append(approvals_pending(self._pending_reviews))
            log_tool_trace(message, trace)
            return format_review_reply(self._pending_reviews)

        if intent is ChatIntent.BLOCKED:
            trace.append(board_list(self._ledger, status="blocked"))
            log_tool_trace(message, trace)
            blocked = self._ledger.list_tasks(status="blocked")
            if not blocked:
                return ChatReply(
                    message="Nie ma zablokowanych zadań na tablicy. Wszystko płynie — sprawdź `#Board`.",
                    suggested_hash="#Board",
                )
            lines = [f"- **{task.team}**: {task.title}" for task in blocked]
            return ChatReply(
                message="Zablokowane zadania:\n\n" + "\n".join(lines) + "\n\n→ `#Board`",
                suggested_hash="#Board",
            )

        if intent is ChatIntent.GENERATE_PLAN:
            items = generate_daily_plan(self._ledger)
            lines = [f"{index + 1}. {item.title}" for index, item in enumerate(items)]
            return ChatReply(
                message="Przygotowałam plan dnia:\n\n" + "\n".join(lines) + "\n\n→ `#Planning`",
                suggested_hash="#Planning",
            )

        if intent is ChatIntent.PLAN_TODAY:
            tool = plan_today(self._ledger)
            trace.append(tool)
            log_tool_trace(message, trace)
            if tool.row_count:
                return ChatReply(message=tool.summary + "\n\n→ `#Planning`", suggested_hash="#Planning")
            return ChatReply(
                message=(
                    "Plan na dziś jest pusty. Napisz „wygeneruj plan” albo kliknij „Generuj plan” w `#Planning`."
                    "\n\n→ `#Planning`"
                ),
                suggested_hash="#Planning",
            )

        search_tool, citations, chunks = await knowledge_search(self._search_backend, message)
        trace.append(search_tool)
        log_tool_trace(message, trace)

        llm_reply = await self._try_llm_reply(message, chunks, citations, tool_summaries=[search_tool.summary])
        if llm_reply is not None:
            return llm_reply

        if chunks:
            return self._template_rag_reply(message, chunks, citations)

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

    def _template_rag_reply(
        self,
        message: str,
        chunks: list[RetrievedChunk],
        citations: list[str],
    ) -> ChatReply:
        lowered = message.lower()
        top = chunks[0]
        excerpt = top.chunk.text[:280].strip()
        if len(top.chunk.text) > 280:
            excerpt += "…"
        source = top.chunk.metadata.source if top.chunk.metadata else "Knowledge"
        reply = f"Znalazłam w Kanonie (**{source}**):\n\n> {excerpt}\n\nPełny kontekst w `#Wiki`."
        if "backup" in lowered or "qdrant" in lowered:
            reply += "\n\n→ `#Wiki` · runbook Operacje/serwer"
        else:
            reply += "\n\n→ `#Wiki`"
        return ChatReply(message=reply, suggested_hash="#Wiki", citations=tuple(citations))

    async def _try_llm_reply(
        self,
        message: str,
        chunks: list[RetrievedChunk],
        citations: list[str],
        *,
        tool_summaries: list[str] | None = None,
    ) -> ChatReply | None:
        if self._chat is None or not self._chat.is_available():
            return None

        context_blocks: list[tuple[str, str]] = []
        for item in chunks[:5]:
            source = item.chunk.metadata.source if item.chunk.metadata else "Knowledge"
            context_blocks.append((source, item.chunk.text[:1200]))

        try:
            reply_text = sanitize_llm_reply(
                await self._chat.complete(build_rag_messages(message, context_blocks, tool_summaries=tool_summaries))
            )
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
