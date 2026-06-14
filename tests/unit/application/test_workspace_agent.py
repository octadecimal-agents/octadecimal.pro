import pytest

from secure_agentic_ai.application.use_cases import IngestDocumentUseCase, RetrieveContextUseCase
from secure_agentic_ai.application.workspace_agent import WorkspaceAgent
from secure_agentic_ai.infrastructure.knowledge.fake_embedding_provider import FakeEmbeddingProvider
from secure_agentic_ai.infrastructure.knowledge.in_memory_vector_store import InMemoryVectorStore
from secure_agentic_ai.infrastructure.workspace.ledger import WorkspaceLedger


@pytest.fixture
def agent(tmp_path):
    ledger = WorkspaceLedger(tmp_path / "ledger.sqlite")
    store = InMemoryVectorStore()
    embedding = FakeEmbeddingProvider()
    ingest = IngestDocumentUseCase(embedding_provider=embedding, vector_store=store)
    retrieve = RetrieveContextUseCase(embedding_provider=embedding, vector_store=store)
    return WorkspaceAgent(ledger=ledger, retrieve=retrieve), ingest


@pytest.mark.asyncio
async def test_chat_suggests_planning(agent) -> None:
    workspace_agent, _ingest = agent
    reply = await workspace_agent.chat("Jaki plan na dziś?")
    assert "#Planning" in (reply.suggested_hash or "")
    assert "plan" in reply.message.lower()


@pytest.mark.asyncio
async def test_chat_blocked_tasks(agent) -> None:
    workspace_agent, _ingest = agent
    workspace_agent._ledger.create_task("automation", "Blocked item", status="blocked")
    reply = await workspace_agent.chat("Co jest zablokowane?")
    assert "Blocked item" in reply.message
    assert reply.suggested_hash == "#Board"


@pytest.mark.asyncio
async def test_chat_rag_citation(agent) -> None:
    workspace_agent, ingest = agent
    await ingest.execute(
        document_id="backup-doc",
        text="Automatyczny backup stacku HYDRA na pc-ubuntu Qdrant backup retention 30 days",
        source="01-Base-Point/pro/servers/pc-ubuntu/Backup.md",
    )
    reply = await workspace_agent.chat("jak backup Qdrant?")
    assert "Backup.md" in "".join(reply.citations) or "Backup.md" in reply.message
    assert reply.suggested_hash == "#Wiki"
