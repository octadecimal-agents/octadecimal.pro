from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ApprovalRequestRow(Base):
    __tablename__ = "approval_requests"

    request_id: Mapped[str] = mapped_column(String(120), primary_key=True)
    actor_id: Mapped[str] = mapped_column(String(120), nullable=False)
    actor_type: Mapped[str] = mapped_column(String(20), nullable=False)
    actor_display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(10), nullable=False)
    action_description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditEventRow(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(120), nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    request_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
