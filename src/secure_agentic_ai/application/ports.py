from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Protocol

from secure_agentic_ai.domain.approvals import ApprovalRequest
from secure_agentic_ai.domain.audit import AuditEvent
from secure_agentic_ai.domain.safety import SafetyVerdict
from secure_agentic_ai.domain.secrets import SecretValue


class ApprovalRequestRepository(Protocol):
    async def save(self, request: ApprovalRequest) -> None: ...

    async def find_by_id(self, request_id: str) -> ApprovalRequest | None: ...

    async def list_pending(self) -> list[ApprovalRequest]: ...


class AuditWriter(Protocol):
    async def record(self, event: AuditEvent) -> None: ...


class EmbeddingProvider(Protocol):
    async def embed(self, text: str) -> list[float]: ...


class VectorStore(Protocol):
    async def upsert(self, chunk_id: str, vector: list[float], metadata: dict[str, str]) -> None: ...

    async def similarity_search(
        self, query_vector: list[float], k: int = 5
    ) -> list[tuple[str, float, dict[str, str]]]: ...


class SafetyChecker(Protocol):
    async def check(self, content: str) -> SafetyVerdict: ...


class Tracer(Protocol):
    @asynccontextmanager
    async def span(self, name: str, attributes: dict[str, str] | None = None) -> AsyncGenerator[None]: ...


class AuditReader(Protocol):
    async def list_recent(self, limit: int = 50) -> list[AuditEvent]: ...


class SecretProvider(Protocol):
    async def resolve(self, name: str) -> SecretValue: ...
