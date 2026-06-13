from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from secure_agentic_ai.adapters.api.app import create_app
from secure_agentic_ai.adapters.api.dependencies import get_request_action_use_case
from secure_agentic_ai.application.use_cases import RequestActionUseCase
from secure_agentic_ai.domain.approvals import ApprovalRequest
from secure_agentic_ai.domain.audit import AuditEvent


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
def client() -> Iterator[TestClient]:
    app = create_app()
    repository = FakeApprovalRequestRepository()
    audit_writer = FakeAuditWriter()

    def use_case_override() -> RequestActionUseCase:
        return RequestActionUseCase(
            request_repository=repository,
            audit_writer=audit_writer,
        )

    app.dependency_overrides[get_request_action_use_case] = use_case_override

    with TestClient(app) as test_client:
        yield test_client


def test_health_check_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_request_action_allows_low_risk_human_action(client: TestClient) -> None:
    response = client.post(
        "/actions",
        json={
            "request_id": "req-001",
            "actor_id": "human-001",
            "actor_type": "human",
            "actor_display_name": "Human Reviewer",
            "action_type": "content.create",
            "risk_level": "low",
            "action_description": "Create documentation draft",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "allowed",
        "decision": "allow",
        "reason": "Action is allowed by the baseline domain policy",
        "approval_request_id": None,
    }


def test_request_action_requires_approval_for_high_risk_agent_action(client: TestClient) -> None:
    response = client.post(
        "/actions",
        json={
            "request_id": "req-002",
            "actor_id": "agent-001",
            "actor_type": "agent",
            "actor_display_name": "Developer Agent",
            "action_type": "file.write",
            "risk_level": "high",
            "action_description": "Write generated source file",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "approval_required",
        "decision": "require_approval",
        "reason": "High-risk agent actions require human approval",
        "approval_request_id": "req-002",
    }


def test_request_action_denies_agent_secret_resolution(client: TestClient) -> None:
    response = client.post(
        "/actions",
        json={
            "request_id": "req-003",
            "actor_id": "agent-001",
            "actor_type": "agent",
            "actor_display_name": "Developer Agent",
            "action_type": "secret.resolve",
            "risk_level": "high",
            "action_description": "Resolve provider token",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "denied",
        "decision": "deny",
        "reason": "Agents cannot resolve secrets directly",
        "approval_request_id": None,
    }


def test_request_action_rejects_invalid_payload(client: TestClient) -> None:
    response = client.post(
        "/actions",
        json={
            "request_id": "",
            "actor_id": "agent-001",
            "actor_type": "robot",
            "actor_display_name": "Developer Agent",
            "action_type": "file.write",
            "risk_level": "high",
            "action_description": "Write generated source file",
        },
    )

    assert response.status_code == 422
