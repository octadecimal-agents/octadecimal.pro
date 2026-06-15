from pathlib import Path

import pytest

from secure_agentic_ai.application.use_cases import IngestDocumentUseCase, RetrieveContextUseCase
from secure_agentic_ai.application.workspace_agent import WorkspaceAgent
from secure_agentic_ai.application.workspace_eval_runner import (
    load_chat_eval_cases,
    load_rag_eval_cases,
)
from secure_agentic_ai.infrastructure.knowledge.fake_embedding_provider import FakeEmbeddingProvider
from secure_agentic_ai.infrastructure.knowledge.in_memory_vector_store import InMemoryVectorStore
from secure_agentic_ai.infrastructure.workspace.hybrid_search import HybridKnowledgeSearch
from secure_agentic_ai.infrastructure.workspace.ledger import WorkspaceLedger

EVALS = Path(__file__).resolve().parents[1] / "evals"


@pytest.mark.asyncio
async def test_workspace_chat_eval_dataset_passes(tmp_path: Path) -> None:
    from secure_agentic_ai.application.workspace_eval_runner import evaluate_chat_case, summarize_results

    ledger = WorkspaceLedger(tmp_path / "ledger.sqlite")
    store = InMemoryVectorStore()
    embedding = FakeEmbeddingProvider()
    ingest = IngestDocumentUseCase(embedding_provider=embedding, vector_store=store)
    await ingest.execute(
        document_id="backup-doc",
        text="# Backup Qdrant\n\nAutomatyczny backup stacku HYDRA Qdrant retention na pc-ubuntu dev.",
        source="01-Base-Point/pro/servers/pc-ubuntu/Backup.md",
    )
    from secure_agentic_ai.application.review_queue import PendingReviewItem

    pending = (
        PendingReviewItem(
            request_id="eval-1",
            description="Deploy to staging",
            actor_display_name="Deploy Agent",
            risk_level="high",
            action_type="run_command",
        ),
    )
    hybrid = HybridKnowledgeSearch(retrieve=RetrieveContextUseCase(embedding, store))
    agent = WorkspaceAgent(ledger=ledger, search=hybrid, pending_reviews=pending)

    results = []
    for case in load_chat_eval_cases(EVALS / "workspace_chat.yaml"):
        reply = await agent.chat(case.input)
        results.append(evaluate_chat_case(case, reply))

    report = summarize_results(results)
    assert report.pass_rate >= 0.8, report.results


@pytest.mark.asyncio
async def test_rag_golden_eval_dataset_passes() -> None:
    from secure_agentic_ai.application.workspace_eval_runner import evaluate_rag_case, summarize_results
    from secure_agentic_ai.infrastructure.workspace.knowledge_policy import RetrievalWeights

    corpus = (
        (
            "backup",
            "01-Base-Point/pro/servers/pc-ubuntu/Backup.md",
            "# Backup Qdrant\n\nAutomatyczny backup stacku HYDRA Qdrant retention na pc-ubuntu.",
        ),
        (
            "mvp",
            "01-Base-Point/pro/projects/octa-os/mvp-localhost-m5.md",
            "# Octa OS MVP\n\nOcta Workspace MVP localhost plan dnia CEO hash panels.",
        ),
        (
            "hitl",
            "01-Base-Point/pro/projects/octa-os/research/hitl-approval.md",
            "# HITL Approval\n\nHuman in the loop approval queue operator console policy.",
        ),
        (
            "embed",
            "01-Base-Point/pro/knowledge-embeddings.md",
            "# Embed Knowledge\n\nEmbed knowledge chunks Qdrant manifest sync incremental dev.",
        ),
        (
            "ceo",
            "01-Base-Point/pro/projects/octa-os/research/07-typowy-dzien-ceo.md",
            "# Plan dnia CEO\n\nTypowy dzień CEO plan dnia morning planning retro journal.",
        ),
    )

    store = InMemoryVectorStore()
    embedding = FakeEmbeddingProvider()
    ingest = IngestDocumentUseCase(embedding_provider=embedding, vector_store=store)
    for doc_id, source, text in corpus:
        await ingest.execute(document_id=doc_id, text=text, source=source)

    hybrid = HybridKnowledgeSearch(
        retrieve=RetrieveContextUseCase(embedding, store),
        weights=RetrievalWeights(vector=0.6, path=0.25, heading=0.1, recency=0.05),
    )

    results = []
    for case in load_rag_eval_cases(EVALS / "rag_golden.yaml"):
        hits = await hybrid.search(case.query, k=case.top_k)
        sources = [hit.chunk.metadata.source if hit.chunk.metadata else "" for hit in hits]
        results.append(evaluate_rag_case(case, sources))

    report = summarize_results(results)
    assert report.pass_rate == 1.0, report.results
