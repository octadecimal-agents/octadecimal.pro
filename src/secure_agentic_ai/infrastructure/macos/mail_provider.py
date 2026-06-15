"""Mail provider stub for Workspace MVP — fixture only (no live IMAP in M5.4)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig

MAIL_FIXTURE_FILENAME = "mail-fixture.json"

DEFAULT_MAIL_FIXTURE: tuple[tuple[str, str], ...] = (
    ("recruiter@example.com", "Senior Python Engineer — follow-up"),
    ("team@octadecimal.pl", "Weekly sync notes"),
)


@dataclass(frozen=True)
class MailItem:
    sender: str
    subject: str
    received_at: str | None = None
    source: str = "fixture"


def mail_fixture_path(config: WorkspaceConfig) -> Path:
    return config.octa_state_dir / MAIL_FIXTURE_FILENAME


def _load_fixture_file(path: Path) -> list[MailItem]:
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, list):
        return []
    items: list[MailItem] = []
    for row in data:
        if not isinstance(row, dict):
            continue
        sender = str(row.get("sender", "")).strip()
        subject = str(row.get("subject", "")).strip()
        if not sender or not subject:
            continue
        received_at = row.get("received_at")
        items.append(
            MailItem(
                sender=sender,
                subject=subject,
                received_at=str(received_at) if received_at else None,
                source="fixture-file",
            )
        )
    return items


def fixture_mail_items(config: WorkspaceConfig) -> list[MailItem]:
    from_file = _load_fixture_file(mail_fixture_path(config))
    if from_file:
        return from_file
    return [MailItem(sender=sender, subject=subject, source="fixture") for sender, subject in DEFAULT_MAIL_FIXTURE]


async def list_unread_summary(config: WorkspaceConfig) -> tuple[list[MailItem], str]:
    """Return unread mail summary. Live macOS/IMAP is out of scope for M5.4."""
    _ = config
    items = fixture_mail_items(config)
    source = items[0].source if items else "fixture"
    return items, source
