import asyncio
import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from secure_agentic_ai.adapters.api.app import create_app
from secure_agentic_ai.adapters.api.dependencies import get_request_action_use_case
from secure_agentic_ai.application.use_cases import RequestActionUseCase
from secure_agentic_ai.domain.approvals import ApprovalRequest
from secure_agentic_ai.domain.audit import AuditEvent
from secure_agentic_ai.infrastructure.persistence.models import Base
from secure_agentic_ai.infrastructure.persistence.session import create_engine
from secure_agentic_ai.infrastructure.workspace.state import reset_for_tests


def _prepare_sqlite_database(db_path: Path) -> None:
    database_url = f"sqlite+aiosqlite:///{db_path}"
    os.environ["DATABASE_URL"] = database_url

    async def _create_schema() -> None:
        engine = create_engine(database_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()

    asyncio.run(_create_schema())


class FakeApprovalRequestRepository:
    def __init__(self) -> None:
        self.saved: list[ApprovalRequest] = []

    async def save(self, request: ApprovalRequest) -> None:
        self.saved.append(request)


class FakeAuditWriter:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    async def record(self, event: AuditEvent) -> None:
        self.events.append(event)


@pytest.fixture
def workspace_client(tmp_path: Path) -> Iterator[TestClient]:
    reset_for_tests()
    _prepare_sqlite_database(tmp_path / "approvals.db")
    os.environ["WORKSPACE_ENABLED"] = "1"
    os.environ["OCTA_LEDGER"] = str(tmp_path / "ledger.sqlite")
    os.environ["KNOWLEDGE_ROOT"] = str(tmp_path / "knowledge")
    os.environ["LLM_PROVIDER"] = "dry"
    os.environ.pop("RAG_BACKEND", None)

    knowledge = tmp_path / "knowledge" / "01-Base-Point/pro/servers/pc-ubuntu"
    knowledge.mkdir(parents=True)
    (knowledge / "Backup.md").write_text(
        "# Backup\n\nAutomatyczny backup Qdrant na pc-ubuntu retention 30 dni.",
        encoding="utf-8",
    )

    app = create_app()
    repository = FakeApprovalRequestRepository()
    audit_writer = FakeAuditWriter()

    def use_case_override() -> RequestActionUseCase:
        return RequestActionUseCase(
            request_repository=repository,
            audit_writer=audit_writer,
        )

    app.dependency_overrides[get_request_action_use_case] = use_case_override

    with TestClient(app) as client:
        yield client

    reset_for_tests()
    os.environ.pop("WORKSPACE_ENABLED", None)
    os.environ.pop("DATABASE_URL", None)
    os.environ.pop("OCTA_LEDGER", None)
    os.environ.pop("KNOWLEDGE_ROOT", None)
    os.environ.pop("LLM_PROVIDER", None)
    os.environ.pop("RAG_BACKEND", None)


def test_workspace_index_served(workspace_client: TestClient) -> None:
    response = workspace_client.get("/")
    assert response.status_code == 200
    assert "Octa Workspace" in response.text


def test_workspace_health(workspace_client: TestClient) -> None:
    response = workspace_client.get("/workspace/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["documents_indexed"] >= 1
    assert data["rag_backend"] == "memory"
    assert data["llm_provider"] == "dry"
    assert data["llm_available"] is False  # dry = heuristics, no external LLM
    assert data["review_pending_count"] >= 0
    assert data["calendar_provider"] == "auto"
    assert isinstance(data["calendar_source"], str)


def test_workspace_chat_dry(workspace_client: TestClient) -> None:
    response = workspace_client.post(
        "/workspace/chat",
        json={"message": "jak backup Qdrant?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "message" in body
    assert body["suggested_hash"] == "#Wiki"


def test_board_task_crud(workspace_client: TestClient) -> None:
    create = workspace_client.post(
        "/workspace/board/tasks",
        json={"team": "automation", "title": "Test task MVP"},
    )
    assert create.status_code == 200
    task_id = create.json()["id"]

    listed = workspace_client.get("/workspace/board/tasks")
    assert any(t["id"] == task_id for t in listed.json())

    updated = workspace_client.patch(
        f"/workspace/board/tasks/{task_id}",
        json={"status": "done"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "done"


def test_wiki_search(workspace_client: TestClient) -> None:
    response = workspace_client.get("/workspace/wiki/search", params={"q": "backup Qdrant"})
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) >= 1
    assert any("Backup.md" in r["source"] for r in results)
    assert "vector_score" not in results[0]


def test_wiki_search_debug_retrieval_scores(workspace_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WORKSPACE_DEBUG", "1")
    response = workspace_client.get(
        "/workspace/wiki/search",
        params={"q": "backup Qdrant"},
        headers={"X-Debug-Retrieval": "1"},
    )
    assert response.status_code == 200
    results = response.json()["results"]
    assert results
    assert "vector_score" in results[0]
    assert "keyword_score" in results[0]
    assert "keyword_raw" in results[0]
    assert "heading_score" in results[0]
    assert "recency_score" in results[0]


def test_planning_generate(workspace_client: TestClient) -> None:
    response = workspace_client.post("/workspace/planning/generate")
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 4
    listed = workspace_client.get("/workspace/planning/items")
    assert len(listed.json()) == len(items)


def test_retro_save(workspace_client: TestClient) -> None:
    response = workspace_client.post(
        "/workspace/retro",
        json={
            "went_well": "MVP boot",
            "improve": "More tests",
            "tomorrow": "Board polish",
        },
    )
    assert response.status_code == 200
    path = Path(response.json()["path"])
    assert path.is_file()
    assert "MVP boot" in path.read_text(encoding="utf-8")
