#!/usr/bin/env python3
"""Run Workspace AO chat and RAG eval datasets (dry / in-memory)."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "tests" / "evals"
CHAT_DATASET = EVALS / "workspace_chat.yaml"
RAG_DATASET = EVALS / "rag_golden.yaml"


async def _run_chat_evals(dataset: Path, min_pass_rate: float) -> int:
    import yaml

    from secure_agentic_ai.application.use_cases import IngestDocumentUseCase, RetrieveContextUseCase
    from secure_agentic_ai.application.workspace_agent import WorkspaceAgent
    from secure_agentic_ai.application.workspace_eval_runner import (
        evaluate_chat_case,
        format_report,
        load_chat_eval_cases,
        parse_min_pass_rate,
        summarize_results,
    )
    from secure_agentic_ai.infrastructure.knowledge.fake_embedding_provider import FakeEmbeddingProvider
    from secure_agentic_ai.infrastructure.knowledge.in_memory_vector_store import InMemoryVectorStore
    from secure_agentic_ai.infrastructure.workspace.hybrid_search import HybridKnowledgeSearch
    from secure_agentic_ai.infrastructure.workspace.ledger import WorkspaceLedger

    meta = yaml.safe_load(dataset.read_text(encoding="utf-8"))
    threshold = parse_min_pass_rate(meta.get("min_pass_rate"), min_pass_rate)

    ledger = WorkspaceLedger(ROOT / "data" / "eval-ledger.sqlite")
    store = InMemoryVectorStore()
    embedding = FakeEmbeddingProvider()
    ingest = IngestDocumentUseCase(embedding_provider=embedding, vector_store=store)
    await ingest.execute(
        document_id="backup-doc",
        text="# Backup Qdrant\n\nAutomatyczny backup stacku HYDRA Qdrant retention na pc-ubuntu dev.",
        source="01-Base-Point/pro/servers/pc-ubuntu/Backup.md",
    )
    await ingest.execute(
        document_id="noise",
        text="bash course elearning tutorial lessons exercises for agents",
        source="01-Base-Point/pro/servers/pc-ubuntu/agents-knowledge/bash-tutorial.md",
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
    for case in load_chat_eval_cases(dataset):
        reply = await agent.chat(case.input)
        results.append(evaluate_chat_case(case, reply))

    report = summarize_results(results)
    print(format_report("Workspace chat evals", report))
    return 0 if report.pass_rate >= threshold else 1


async def _run_rag_evals(dataset: Path, min_pass_rate: float) -> int:
    import yaml

    from secure_agentic_ai.application.use_cases import IngestDocumentUseCase, RetrieveContextUseCase
    from secure_agentic_ai.application.workspace_eval_runner import (
        evaluate_rag_case,
        format_report,
        load_rag_eval_cases,
        parse_min_pass_rate,
        summarize_results,
    )
    from secure_agentic_ai.infrastructure.knowledge.fake_embedding_provider import FakeEmbeddingProvider
    from secure_agentic_ai.infrastructure.knowledge.in_memory_vector_store import InMemoryVectorStore
    from secure_agentic_ai.infrastructure.workspace.hybrid_search import HybridKnowledgeSearch
    from secure_agentic_ai.infrastructure.workspace.knowledge_policy import RetrievalWeights

    meta = yaml.safe_load(dataset.read_text(encoding="utf-8"))
    threshold = parse_min_pass_rate(meta.get("min_pass_rate"), min_pass_rate)

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
    for case in load_rag_eval_cases(dataset):
        hits = await hybrid.search(case.query, k=case.top_k)
        sources = [hit.chunk.metadata.source if hit.chunk.metadata else "" for hit in hits]
        results.append(evaluate_rag_case(case, sources))

    report = summarize_results(results)
    print(format_report("RAG golden evals", report))
    return 0 if report.pass_rate >= threshold else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Workspace eval datasets.")
    parser.add_argument("--chat", action="store_true", help="Run workspace_chat.yaml")
    parser.add_argument("--rag", action="store_true", help="Run rag_golden.yaml")
    parser.add_argument("--all", action="store_true", help="Run all datasets")
    parser.add_argument("--dry", action="store_true", help="Alias for --all (no external LLM)")
    parser.add_argument("--min-pass-rate", type=float, default=0.8)
    args = parser.parse_args(argv)

    run_chat = args.chat or args.all or args.dry
    run_rag = args.rag or args.all or args.dry
    if not run_chat and not run_rag:
        run_chat = True
        run_rag = True

    exit_code = 0
    if run_chat:
        exit_code = max(exit_code, asyncio.run(_run_chat_evals(CHAT_DATASET, args.min_pass_rate)))
    if run_rag:
        exit_code = max(exit_code, asyncio.run(_run_rag_evals(RAG_DATASET, args.min_pass_rate)))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
