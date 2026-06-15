import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from secure_agentic_ai.domain.approvals import ApprovalRequest
from secure_agentic_ai.domain.audit import AuditEvent, AuditEventType
from secure_agentic_ai.domain.policies import Action
from secure_agentic_ai.infrastructure.persistence.models import (
    ApprovalRequestRow,
    AuditEventRow,
)


class SqlAlchemyApprovalRequestRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, request: ApprovalRequest) -> None:
        row = ApprovalRequestRow(
            request_id=request.request_id,
            actor_id=request.requested_by.actor_id,
            actor_type=request.requested_by.actor_type.value,
            actor_display_name=request.requested_by.display_name,
            action_type=request.action.action_type.value,
            risk_level=request.action.risk_level.value,
            action_description=request.action.description,
            status=request.status.value,
            requested_at=request.requested_at,
            decided_at=request.decided_at,
        )
        self._session.add(row)
        await self._session.commit()

    async def find_by_id(self, request_id: str) -> ApprovalRequest | None:
        result = await self._session.execute(
            select(ApprovalRequestRow).where(ApprovalRequestRow.request_id == request_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return self._row_to_domain(row)

    async def list_pending(self) -> list[ApprovalRequest]:
        result = await self._session.execute(
            select(ApprovalRequestRow)
            .where(ApprovalRequestRow.status == "pending")
            .order_by(ApprovalRequestRow.requested_at.desc())
        )
        return [self._row_to_domain(row) for row in result.scalars()]

    async def update_status(self, request_id: str, status: str, decided_at: datetime | None) -> None:
        result = await self._session.execute(
            select(ApprovalRequestRow).where(ApprovalRequestRow.request_id == request_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        row.status = status
        row.decided_at = decided_at
        await self._session.commit()

    @staticmethod
    def _row_to_domain(row: ApprovalRequestRow) -> ApprovalRequest:
        from secure_agentic_ai.domain.actors import Actor, ActorType
        from secure_agentic_ai.domain.approvals import ApprovalStatus
        from secure_agentic_ai.domain.policies import ActionType, RiskLevel

        return ApprovalRequest(
            request_id=row.request_id,
            action=Action(
                action_type=ActionType(row.action_type),
                risk_level=RiskLevel(row.risk_level),
                description=row.action_description,
            ),
            requested_by=Actor(
                actor_id=row.actor_id,
                actor_type=ActorType(row.actor_type),
                display_name=row.actor_display_name,
            ),
            status=ApprovalStatus(row.status),
            requested_at=row.requested_at,
            decided_at=row.decided_at,
        )


class SqlAlchemyAuditWriter:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(self, event: AuditEvent) -> None:
        row = AuditEventRow(
            event_id=event.event_id,
            event_type=event.event_type.value,
            actor_id=event.actor_id,
            action_type=event.action_type,
            request_id=event.request_id,
            timestamp=event.timestamp,
            metadata_json=json.dumps(event.metadata) if event.metadata else None,
        )
        self._session.add(row)
        await self._session.commit()


class SqlAlchemyAuditReader:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_recent(self, limit: int = 50) -> list[AuditEvent]:
        result = await self._session.execute(
            select(AuditEventRow).order_by(AuditEventRow.timestamp.desc()).limit(limit)
        )
        events: list[AuditEvent] = []
        for row in result.scalars():
            events.append(
                AuditEvent(
                    event_id=row.event_id,
                    event_type=AuditEventType(row.event_type),
                    actor_id=row.actor_id,
                    action_type=row.action_type,
                    request_id=row.request_id,
                    timestamp=row.timestamp,
                    metadata=json.loads(row.metadata_json) if row.metadata_json else {},
                )
            )
        return events
