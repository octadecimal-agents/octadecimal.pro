from dataclasses import dataclass
from enum import StrEnum
from uuid import uuid4

from secure_agentic_ai.application.commands import RequestActionCommand, ResolveSecretCommand
from secure_agentic_ai.application.ports import (
    ApprovalRequestRepository,
    AuditWriter,
    EmbeddingProvider,
    SafetyChecker,
    SecretProvider,
    Tracer,
    VectorStore,
)
from secure_agentic_ai.domain.approvals import ApprovalRequest
from secure_agentic_ai.domain.audit import AuditEvent, AuditEventType
from secure_agentic_ai.domain.knowledge import ChunkMetadata, DocumentChunk, RetrievedChunk
from secure_agentic_ai.domain.policies import (
    Action,
    ActionType,
    PolicyDecision,
    PolicyEvaluation,
    RiskLevel,
    evaluate_policy,
)
from secure_agentic_ai.domain.safety import SafetyRiskLevel, SafetyVerdict
from secure_agentic_ai.domain.secrets import SecretValue


class RequestActionStatus(StrEnum):
    ALLOWED = "allowed"
    APPROVAL_REQUIRED = "approval_required"
    DENIED = "denied"


@dataclass(frozen=True)
class RequestActionResult:
    status: RequestActionStatus
    evaluation: PolicyEvaluation
    approval_request: ApprovalRequest | None = None


class RequestActionUseCase:
    def __init__(
        self,
        request_repository: ApprovalRequestRepository,
        audit_writer: AuditWriter,
        safety_checker: SafetyChecker | None = None,
        tracer: Tracer | None = None,
    ) -> None:
        self.request_repository = request_repository
        self.audit_writer = audit_writer
        self.safety_checker = safety_checker
        self.tracer = tracer

    async def _record_audit(
        self, event_type: AuditEventType, command: RequestActionCommand, request_id: str | None = None
    ) -> None:
        trace_id = self.tracer.trace_id if self.tracer else None
        trace_id = str(trace_id) if trace_id is not None else None
        event = AuditEvent(
            event_id=str(uuid4()),
            event_type=event_type,
            actor_id=command.actor.actor_id,
            action_type=command.action.action_type.value,
            request_id=request_id,
            trace_id=trace_id,
        )
        await self.audit_writer.record(event)

    async def _check_safety(self, command: RequestActionCommand) -> SafetyVerdict | None:
        if self.safety_checker is None:
            return None
        return await self.safety_checker.check(command.action.description)

    async def execute(self, command: RequestActionCommand) -> RequestActionResult:
        if self.tracer:
            async with self.tracer.span(
                "RequestActionUseCase.execute",
                attributes={"actor_id": command.actor.actor_id, "action_type": command.action.action_type.value},
            ):
                return await self._execute(command)
        return await self._execute(command)

    async def _execute(self, command: RequestActionCommand) -> RequestActionResult:
        verdict = await self._check_safety(command)
        if verdict is not None and verdict.risk_level == SafetyRiskLevel.DANGEROUS:
            denial = PolicyEvaluation(
                decision=PolicyDecision.DENY,
                reason=f"Action blocked by safety check: {verdict.reason}",
            )
            await self._record_audit(AuditEventType.ACTION_DENIED, command)
            return RequestActionResult(
                status=RequestActionStatus.DENIED,
                evaluation=denial,
            )

        if verdict is not None and verdict.risk_level == SafetyRiskLevel.SUSPICIOUS:
            approval_request = ApprovalRequest(
                request_id=command.request_id,
                action=command.action,
                requested_by=command.actor,
            )
            await self.request_repository.save(approval_request)
            await self._record_audit(AuditEventType.APPROVAL_REQUESTED, command, request_id=approval_request.request_id)
            warning = PolicyEvaluation(
                decision=PolicyDecision.REQUIRE_APPROVAL,
                reason=f"Suspicious content requires human review: {verdict.reason}",
            )
            return RequestActionResult(
                status=RequestActionStatus.APPROVAL_REQUIRED,
                evaluation=warning,
                approval_request=approval_request,
            )

        evaluation = evaluate_policy(command.actor, command.action)

        match evaluation.decision:
            case PolicyDecision.ALLOW:
                await self._record_audit(AuditEventType.ACTION_ALLOWED, command)
                return RequestActionResult(
                    status=RequestActionStatus.ALLOWED,
                    evaluation=evaluation,
                )

            case PolicyDecision.REQUIRE_APPROVAL:
                approval_request = ApprovalRequest(
                    request_id=command.request_id,
                    action=command.action,
                    requested_by=command.actor,
                )
                await self.request_repository.save(approval_request)
                await self._record_audit(
                    AuditEventType.APPROVAL_REQUESTED, command, request_id=approval_request.request_id
                )
                return RequestActionResult(
                    status=RequestActionStatus.APPROVAL_REQUIRED,
                    evaluation=evaluation,
                    approval_request=approval_request,
                )

            case PolicyDecision.DENY:
                await self._record_audit(AuditEventType.ACTION_DENIED, command)
                return RequestActionResult(
                    status=RequestActionStatus.DENIED,
                    evaluation=evaluation,
                )


CHUNK_SIZE = 300
CHUNK_OVERLAP = 50


def _split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
        if i >= len(words):
            break
    return chunks


class IngestDocumentUseCase:
    def __init__(self, embedding_provider: EmbeddingProvider, vector_store: VectorStore) -> None:
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store

    async def execute(self, document_id: str, text: str, source: str) -> list[DocumentChunk]:
        raw_chunks = _split_text(text)
        chunks: list[DocumentChunk] = []
        for i, raw in enumerate(raw_chunks):
            chunk = DocumentChunk(
                document_id=document_id,
                text=raw,
                metadata=ChunkMetadata(source=source, document_id=document_id, section=f"chunk-{i}"),
            )
            embedding = await self._embedding_provider.embed(raw)
            await self._vector_store.upsert(
                chunk_id=chunk.chunk_id,
                vector=embedding,
                metadata={
                    "document_id": document_id,
                    "source": source,
                    "section": f"chunk-{i}",
                    "text": raw,
                },
            )
            chunks.append(chunk)
        return chunks


class RetrieveContextUseCase:
    def __init__(self, embedding_provider: EmbeddingProvider, vector_store: VectorStore) -> None:
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store

    async def execute(self, query: str, k: int = 3) -> list[RetrievedChunk]:
        query_embedding = await self._embedding_provider.embed(query)
        results = await self._vector_store.similarity_search(query_embedding, k=k)
        retrieved = []
        for chunk_id, score, metadata in results:
            chunk = DocumentChunk(
                chunk_id=chunk_id,
                document_id=metadata.get("document_id", ""),
                text=metadata.get("text", ""),
                metadata=ChunkMetadata(
                    source=metadata.get("source", ""),
                    document_id=metadata.get("document_id", ""),
                    section=metadata.get("section"),
                ),
            )
            retrieved.append(RetrievedChunk(chunk=chunk, score=score))
        return retrieved


class SecretResolveStatus(StrEnum):
    RESOLVED = "resolved"
    DENIED = "denied"


@dataclass(frozen=True)
class SecretResolveResult:
    status: SecretResolveStatus
    value: SecretValue | None = None
    evaluation: PolicyEvaluation | None = None


class ResolveSecretUseCase:
    def __init__(
        self,
        secret_provider: SecretProvider,
        audit_writer: AuditWriter,
    ) -> None:
        self._secret_provider = secret_provider
        self._audit_writer = audit_writer

    async def _record_audit(self, event_type: AuditEventType, command: ResolveSecretCommand, secret_name: str) -> None:
        event = AuditEvent(
            event_id=str(uuid4()),
            event_type=event_type,
            actor_id=command.actor.actor_id,
            action_type=ActionType.RESOLVE_SECRET.value,
            metadata={"secret_name": secret_name},
        )
        await self._audit_writer.record(event)

    async def execute(self, command: ResolveSecretCommand) -> SecretResolveResult:
        action = Action(
            action_type=ActionType.RESOLVE_SECRET,
            risk_level=RiskLevel.HIGH,
            description=f"Resolve secret: {command.secret_name}",
        )

        evaluation = evaluate_policy(command.actor, action)

        match evaluation.decision:
            case PolicyDecision.DENY:
                await self._record_audit(AuditEventType.ACTION_DENIED, command, command.secret_name)
                return SecretResolveResult(
                    status=SecretResolveStatus.DENIED,
                    evaluation=evaluation,
                )

            case PolicyDecision.REQUIRE_APPROVAL:
                await self._record_audit(AuditEventType.APPROVAL_REQUESTED, command, command.secret_name)
                return SecretResolveResult(
                    status=SecretResolveStatus.DENIED,
                    evaluation=evaluation,
                )

            case PolicyDecision.ALLOW:
                value = await self._secret_provider.resolve(command.secret_name)
                await self._record_audit(AuditEventType.ACTION_ALLOWED, command, command.secret_name)
                return SecretResolveResult(
                    status=SecretResolveStatus.RESOLVED,
                    value=value,
                    evaluation=evaluation,
                )
