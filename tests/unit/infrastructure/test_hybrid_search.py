import pytest

from secure_agentic_ai.application.use_cases import IngestDocumentUseCase, RetrieveContextUseCase
from secure_agentic_ai.infrastructure.knowledge.fake_embedding_provider import FakeEmbeddingProvider
from secure_agentic_ai.infrastructure.knowledge.in_memory_vector_store import InMemoryVectorStore
from secure_agentic_ai.infrastructure.workspace.hybrid_search import HybridKnowledgeSearch, keyword_score


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
        text="Automatyczny backup stacku HYDRA Qdrant retention",
        source="01-Base-Point/pro/servers/pc-ubuntu/Backup.md",
    )
    hybrid = HybridKnowledgeSearch(retrieve=RetrieveContextUseCase(embedding, store))
    results = await hybrid.search("jak backup Qdrant?", k=1)
    assert results
    source = results[0].chunk.metadata.source if results[0].chunk.metadata else ""
    assert "Backup.md" in source
