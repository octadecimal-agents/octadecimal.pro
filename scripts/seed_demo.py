"""Seed demo data: create sample pending approval requests + audit events.

Usage:
  uv run python scripts/seed_demo.py
  uv run python scripts/seed_demo.py --reset
  uv run python scripts/seed_demo.py --force
"""

import argparse
import asyncio
import os
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from secure_agentic_ai.domain.actors import Actor, ActorType
from secure_agentic_ai.domain.approvals import ApprovalRequest
from secure_agentic_ai.domain.audit import AuditEvent, AuditEventType
from secure_agentic_ai.domain.policies import Action, ActionType, RiskLevel
from secure_agentic_ai.infrastructure.persistence.approval_repository import (
    SqlAlchemyApprovalRequestRepository,
    SqlAlchemyAuditWriter,
)
from secure_agentic_ai.infrastructure.persistence.models import ApprovalRequestRow, AuditEventRow, Base

_DEFAULT_DB = "sqlite+aiosqlite:///data/dev.db"
_DEMO_REQUEST_PREFIX = "demo-"


async def _count_demo_approvals(session: AsyncSession) -> int:
    result = await session.execute(
        select(ApprovalRequestRow).where(ApprovalRequestRow.request_id.like(f"{_DEMO_REQUEST_PREFIX}%"))
    )
    return len(result.scalars().all())


async def _clear_demo_data(session: AsyncSession) -> None:
    await session.execute(delete(AuditEventRow).where(AuditEventRow.request_id.like(f"{_DEMO_REQUEST_PREFIX}%")))
    await session.execute(delete(AuditEventRow).where(AuditEventRow.request_id == "demo-deny-001"))
    await session.execute(
        delete(ApprovalRequestRow).where(ApprovalRequestRow.request_id.like(f"{_DEMO_REQUEST_PREFIX}%"))
    )
    await session.commit()


async def seed(*, reset: bool = False, force: bool = False) -> None:
    database_url = os.environ.get("DATABASE_URL", _DEFAULT_DB)
    engine = create_async_engine(database_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        if reset:
            await _clear_demo_data(session)
            print("  Cleared existing demo approvals and related audit rows.")

        if not reset and not force:
            existing = await _count_demo_approvals(session)
            if existing > 0:
                print(f"  Demo data already present ({existing} approvals) — skip. Use --reset or --force.")
                await engine.dispose()
                return

        repo = SqlAlchemyApprovalRequestRepository(session)
        audit = SqlAlchemyAuditWriter(session)

        scenarios = [
            (
                "Write generated source file",
                ActionType.WRITE_FILE,
                RiskLevel.HIGH,
                Actor(actor_id="agent-001", actor_type=ActorType.AGENT, display_name="Dev Agent"),
            ),
            (
                "Deploy to staging environment",
                ActionType.RUN_COMMAND,
                RiskLevel.HIGH,
                Actor(actor_id="agent-002", actor_type=ActorType.AGENT, display_name="Deploy Agent"),
            ),
            (
                "Send notification to #security channel",
                ActionType.SEND_NOTIFICATION,
                RiskLevel.MEDIUM,
                Actor(actor_id="agent-003", actor_type=ActorType.AGENT, display_name="Monitor Agent"),
            ),
        ]

        for desc, action_type, risk_level, actor in scenarios:
            action = Action(action_type=action_type, risk_level=risk_level, description=desc)
            request = ApprovalRequest(
                request_id=f"demo-{uuid4().hex[:8]}",
                action=action,
                requested_by=actor,
            )
            await repo.save(request)

            event = AuditEvent(
                event_id=str(uuid4()),
                event_type=AuditEventType.APPROVAL_REQUESTED,
                actor_id=actor.actor_id,
                action_type=action_type.value,
                request_id=request.request_id,
            )
            await audit.record(event)
            print(f"  Created: {request.request_id} — {desc}")

        audit_entries = [
            AuditEvent(
                event_id=str(uuid4()),
                event_type=AuditEventType.ACTION_ALLOWED,
                actor_id="human-001",
                action_type=ActionType.READ_CONTEXT.value,
            ),
            AuditEvent(
                event_id=str(uuid4()),
                event_type=AuditEventType.ACTION_DENIED,
                actor_id="agent-001",
                action_type=ActionType.RESOLVE_SECRET.value,
                request_id="demo-deny-001",
            ),
        ]
        for event in audit_entries:
            await audit.record(event)
            print(f"  Audited: {event.event_id} — {event.event_type.value}")

        print(f"\nDone. {len(scenarios)} approvals + {len(audit_entries)} extra audit events created.")

    await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo HITL approvals for local dev.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Remove existing demo-* approvals (and related audit rows) before seeding.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Seed even when demo approvals already exist (may duplicate pending items).",
    )
    args = parser.parse_args()
    print("Seeding demo data...")
    asyncio.run(seed(reset=args.reset, force=args.force))


if __name__ == "__main__":
    main()
