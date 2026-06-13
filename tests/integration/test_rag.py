import pytest

from secure_agentic_ai.application.use_cases import IngestDocumentUseCase, RetrieveContextUseCase
from secure_agentic_ai.infrastructure.knowledge.fake_embedding_provider import FakeEmbeddingProvider
from secure_agentic_ai.infrastructure.knowledge.in_memory_vector_store import InMemoryVectorStore
from secure_agentic_ai.infrastructure.knowledge.synthetic_dataset import DOCUMENTS


@pytest.fixture
def embedding_provider():
    return FakeEmbeddingProvider()


@pytest.fixture
def vector_store():
    return InMemoryVectorStore()


@pytest.mark.asyncio
async def test_ingest_documents(embedding_provider, vector_store):
    use_case = IngestDocumentUseCase(embedding_provider=embedding_provider, vector_store=vector_store)

    chunks = await use_case.execute(
        document_id="doc-001",
        text=DOCUMENTS[0],
        source="synthetic/policies.txt",
    )

    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.document_id == "doc-001"
        assert chunk.text
        assert chunk.metadata is not None
        assert chunk.metadata.source == "synthetic/policies.txt"


@pytest.mark.asyncio
async def test_retrieve_returns_results(embedding_provider, vector_store):
    ingest = IngestDocumentUseCase(embedding_provider=embedding_provider, vector_store=vector_store)

    for i, doc in enumerate(DOCUMENTS):
        await ingest.execute(document_id=f"doc-{i:03d}", text=doc, source="synthetic")

    retrieve = RetrieveContextUseCase(embedding_provider=embedding_provider, vector_store=vector_store)

    results = await retrieve.execute("policy", k=4)

    assert len(results) == 4
    for r in results:
        assert r.score > 0
        assert r.chunk.text


@pytest.mark.asyncio
async def test_retrieve_returns_top_k(embedding_provider, vector_store):
    ingest = IngestDocumentUseCase(embedding_provider=embedding_provider, vector_store=vector_store)

    for i, doc in enumerate(DOCUMENTS):
        await ingest.execute(document_id=f"doc-{i:03d}", text=doc, source="synthetic")

    retrieve = RetrieveContextUseCase(embedding_provider=embedding_provider, vector_store=vector_store)

    results = await retrieve.execute("policy evaluation", k=3)

    assert len(results) <= 3
    for r in results:
        assert r.score > 0


@pytest.mark.asyncio
async def test_retrieve_empty_store(embedding_provider, vector_store):
    retrieve = RetrieveContextUseCase(embedding_provider=embedding_provider, vector_store=vector_store)

    results = await retrieve.execute("anything", k=5)

    assert results == []


@pytest.mark.asyncio
async def test_split_text():
    from secure_agentic_ai.application.use_cases import _split_text

    text = "word " * 1000
    chunks = _split_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert all(len(c.split()) <= 100 for c in chunks)
