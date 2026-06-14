import pytest

from secure_agentic_ai.infrastructure.knowledge.qdrant_vector_store import QdrantVectorStore


@pytest.fixture
async def qdrant_store() -> QdrantVectorStore:
    store = QdrantVectorStore(url=":memory:", collection="test_knowledge")
    await store.ensure_collection()
    yield store
    await store.close()


@pytest.mark.asyncio
async def test_qdrant_upsert_and_search(qdrant_store: QdrantVectorStore) -> None:
    vector_a = [1.0, 0.0, 0.0] + [0.0] * 61
    vector_b = [0.9, 0.1, 0.0] + [0.0] * 61
    vector_query = [1.0, 0.0, 0.0] + [0.0] * 61

    await qdrant_store.upsert(
        "chunk-a",
        vector_a,
        {"document_id": "doc-a", "source": "a.md", "section": "chunk-0", "text": "alpha"},
    )
    await qdrant_store.upsert(
        "chunk-b",
        vector_b,
        {"document_id": "doc-b", "source": "b.md", "section": "chunk-0", "text": "beta"},
    )

    hits = await qdrant_store.similarity_search(vector_query, k=2)
    assert len(hits) == 2
    assert hits[0][0] == "chunk-a"
    assert hits[0][2]["source"] == "a.md"


@pytest.mark.asyncio
async def test_qdrant_count_points(qdrant_store: QdrantVectorStore) -> None:
    assert await qdrant_store.count_points() == 0
    vector = [0.1] * 64
    await qdrant_store.upsert("chunk-1", vector, {"source": "x.md", "text": "hello"})
    assert await qdrant_store.count_points() == 1
