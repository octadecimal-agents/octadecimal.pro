import pytest

from secure_agentic_ai.application.review_queue import PendingReviewItem
from secure_agentic_ai.application.use_cases import IngestDocumentUseCase, RetrieveContextUseCase
from secure_agentic_ai.application.workspace_agent import WorkspaceAgent
from secure_agentic_ai.infrastructure.knowledge.fake_embedding_provider import FakeEmbeddingProvider
from secure_agentic_ai.infrastructure.knowledge.in_memory_vector_store import InMemoryVectorStore
from secure_agentic_ai.infrastructure.workspace.hybrid_search import HybridKnowledgeSearch
from secure_agentic_ai.infrastructure.workspace.ledger import WorkspaceLedger


@pytest.fixture
def agent(tmp_path):
    ledger = WorkspaceLedger(tmp_path / "ledger.sqlite")
    store = InMemoryVectorStore()
    embedding = FakeEmbeddingProvider()
    ingest = IngestDocumentUseCase(embedding_provider=embedding, vector_store=store)
    retrieve = RetrieveContextUseCase(embedding_provider=embedding, vector_store=store)
    hybrid = HybridKnowledgeSearch(retrieve=retrieve)
    return WorkspaceAgent(ledger=ledger, search=hybrid), ingest


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
        document_id="noise",
        text="bash course elearning tutorial",
        source="01-Base-Point/pro/servers/pc-ubuntu/agents-knowledge/bash-tutorial.md",
    )
    await ingest.execute(
        document_id="backup-doc",
        text="Automatyczny backup stacku HYDRA na pc-ubuntu Qdrant backup retention 30 days",
        source="01-Base-Point/pro/servers/pc-ubuntu/Backup.md",
    )
    reply = await workspace_agent.chat("jak backup Qdrant?")
    assert "Backup.md" in "".join(reply.citations) or "Backup.md" in reply.message
    assert reply.suggested_hash == "#Wiki"


@pytest.mark.asyncio
async def test_chat_generate_plan(agent) -> None:
    workspace_agent, _ingest = agent
    reply = await workspace_agent.chat("wygeneruj plan na dziś")
    assert "#Planning" in (reply.suggested_hash or "")
    assert "Sprint planning" in reply.message or "Deep work" in reply.message


@pytest.mark.asyncio
async def test_chat_review_queue(agent) -> None:
    workspace_agent, _ingest = agent
    pending = (
        PendingReviewItem(
            request_id="demo-1",
            description="Deploy to staging",
            actor_display_name="Deploy Agent",
            risk_level="high",
            action_type="run_command",
        ),
    )
    agent_with_review = WorkspaceAgent(
        ledger=workspace_agent._ledger,
        search=workspace_agent._search_backend,
        pending_reviews=pending,
    )
    reply = await agent_with_review.chat("Co czeka w review?")
    assert reply.suggested_hash == "#Review"
    assert "Deploy to staging" in reply.message


@pytest.mark.asyncio
async def test_chat_attention_summary(agent) -> None:
    workspace_agent, _ingest = agent
    workspace_agent._ledger.create_task("security", "Fix policy gate", status="blocked")
    pending = (
        PendingReviewItem(
            request_id="demo-1",
            description="Write generated source file",
            actor_display_name="Dev Agent",
            risk_level="high",
            action_type="write_file",
        ),
    )
    agent_with_review = WorkspaceAgent(
        ledger=workspace_agent._ledger,
        search=workspace_agent._search_backend,
        pending_reviews=pending,
    )
    reply = await agent_with_review.chat("Co wymaga uwagi?")
    assert reply.suggested_hash == "#Review"
    assert "Write generated source file" in reply.message
    assert "Fix policy gate" in reply.message
