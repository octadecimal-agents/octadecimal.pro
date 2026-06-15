from pathlib import Path

import pytest

from secure_agentic_ai.application.use_cases import IngestDocumentUseCase, RetrieveContextUseCase
from secure_agentic_ai.infrastructure.knowledge.fake_embedding_provider import FakeEmbeddingProvider
from secure_agentic_ai.infrastructure.knowledge.in_memory_vector_store import InMemoryVectorStore
from secure_agentic_ai.infrastructure.workspace.hybrid_search import (
    HybridKnowledgeSearch,
    heading_score,
    keyword_score,
)
from secure_agentic_ai.infrastructure.workspace.knowledge_policy import RetrievalWeights
from secure_agentic_ai.infrastructure.workspace.retrieval_log import log_retrieval_query

GOLDEN_CORPUS: tuple[tuple[str, str, str], ...] = (
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

GOLDEN_QUERIES: tuple[tuple[str, str], ...] = (
    ("backup Qdrant", "Backup.md"),
    ("Octa OS MVP", "mvp-localhost-m5.md"),
    ("HITL approval", "hitl-approval.md"),
    ("embed knowledge", "knowledge-embeddings.md"),
    ("plan dnia CEO", "07-typowy-dzien-ceo.md"),
)

V2_WEIGHTS = RetrievalWeights(vector=0.6, path=0.25, heading=0.1, recency=0.05)


async def _build_hybrid(tmp_path: Path) -> HybridKnowledgeSearch:
    root = tmp_path / "knowledge"
    store = InMemoryVectorStore()
    embedding = FakeEmbeddingProvider()
    ingest = IngestDocumentUseCase(embedding_provider=embedding, vector_store=store)
    for doc_id, source, text in GOLDEN_CORPUS:
        path = root / source
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        await ingest.execute(document_id=doc_id, text=text, source=source)
    return HybridKnowledgeSearch(
        retrieve=RetrieveContextUseCase(embedding, store),
        weights=V2_WEIGHTS,
        knowledge_root=root,
    )


def test_keyword_score_boosts_filename() -> None:
    score = keyword_score(
        "backup Qdrant",
        "01-Base-Point/pro/servers/pc-ubuntu/Backup.md",
        "some unrelated text",
    )
    assert score > keyword_score(
        "backup Qdrant",
        "01-Base-Point/pro/servers/pc-ubuntu/agents-knowledge/bash-tutorial.md",
        "backup backup backup",
    )


def test_heading_score_matches_markdown_headings() -> None:
    text = "# Backup Qdrant\n\nBody text without keywords in heading."
    assert heading_score("backup Qdrant", text) == 1.0
    assert heading_score("unrelated topic", text) == 0.0


@pytest.mark.asyncio
async def test_hybrid_search_prefers_backup_doc() -> None:
    store = InMemoryVectorStore()
    embedding = FakeEmbeddingProvider()
    ingest = IngestDocumentUseCase(embedding_provider=embedding, vector_store=store)
    await ingest.execute(
        document_id="noise",
        text="bash course elearning tutorial lessons exercises",
        source="01-Base-Point/pro/servers/pc-ubuntu/agents-knowledge/bash-tutorial.md",
    )
    await ingest.execute(
        document_id="backup",
        text="# Backup Qdrant\n\nAutomatyczny backup stacku HYDRA Qdrant retention",
        source="01-Base-Point/pro/servers/pc-ubuntu/Backup.md",
    )
    hybrid = HybridKnowledgeSearch(retrieve=RetrieveContextUseCase(embedding, store))
    results = await hybrid.search("jak backup Qdrant?", k=1)
    assert results
    source = results[0].chunk.metadata.source if results[0].chunk.metadata else ""
    assert "Backup.md" in source


@pytest.mark.asyncio
async def test_hybrid_search_includes_score_breakdown(tmp_path: Path) -> None:
    hybrid = await _build_hybrid(tmp_path)
    results = await hybrid.search("backup Qdrant", k=1)
    assert results
    breakdown = results[0].breakdown
    assert breakdown is not None
    assert breakdown.vector_score >= 0.0
    assert breakdown.keyword_score >= 0.0
    assert breakdown.heading_score >= 0.0
    assert breakdown.combined_score == pytest.approx(results[0].score)


@pytest.mark.parametrize(("query", "expected_suffix"), GOLDEN_QUERIES)
@pytest.mark.asyncio
async def test_golden_queries_surface_expected_source_in_top3(tmp_path: Path, query: str, expected_suffix: str) -> None:
    hybrid = await _build_hybrid(tmp_path)
    results = await hybrid.search(query, k=3)
    sources = [hit.chunk.metadata.source if hit.chunk.metadata else "" for hit in results]
    assert any(expected_suffix in source for source in sources), f"{query!r} -> {sources}"


@pytest.mark.parametrize(("query", "expected_suffix"), GOLDEN_QUERIES)
@pytest.mark.asyncio
async def test_golden_queries_rank_expected_source_first(tmp_path: Path, query: str, expected_suffix: str) -> None:
    hybrid = await _build_hybrid(tmp_path)
    results = await hybrid.search(query, k=1)
    assert results
    source = results[0].chunk.metadata.source if results[0].chunk.metadata else ""
    assert expected_suffix in source, f"{query!r} -> {source}"


def test_log_retrieval_query_emits_json(caplog: pytest.LogCaptureFixture) -> None:
    import logging

    from secure_agentic_ai.domain.knowledge import ChunkMetadata, DocumentChunk, RetrievalScoreBreakdown

    caplog.set_level(logging.INFO, logger="secure_agentic_ai.retrieval")
    chunk = DocumentChunk(
        document_id="backup",
        text="backup Qdrant",
        metadata=ChunkMetadata(source="01-Base-Point/pro/servers/pc-ubuntu/Backup.md", document_id="backup"),
    )
    from secure_agentic_ai.domain.knowledge import RetrievedChunk

    hits = [
        RetrievedChunk(
            chunk=chunk,
            score=0.91,
            breakdown=RetrievalScoreBreakdown(
                vector_score=0.2,
                keyword_score=0.95,
                keyword_raw=3.5,
                heading_score=0.8,
                recency_score=0.5,
                combined_score=0.91,
            ),
        )
    ]
    log_retrieval_query("backup Qdrant", hits)
    assert any('"event": "retrieval"' in record.message for record in caplog.records)
    assert any("Backup.md" in record.message for record in caplog.records)
