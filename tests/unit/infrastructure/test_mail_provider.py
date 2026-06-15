import pytest

from secure_agentic_ai.infrastructure.macos.mail_provider import fixture_mail_items, list_unread_summary
from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig


def _config(tmp_path) -> WorkspaceConfig:
    root = tmp_path / "knowledge"
    root.mkdir()
    return WorkspaceConfig(
        enabled=True,
        knowledge_root=root,
        ledger_path=tmp_path / "ledger.sqlite",
        journal_dir=root / "journal",
        llm_provider="dry",
        deepseek_model="deepseek-v4-flash",
        deepseek_base_url="https://api.deepseek.com",
        deepseek_bw_label="",
        minimax_model="MiniMax-M3",
        minimax_base_url="https://api.minimax.io/v1",
        minimax_bw_label="",
        calendar_provider="fixture",
        calendar_fixture_path=tmp_path / "calendar.json",
        calendar_include=(),
        calendar_exclude=(),
        octa_state_dir=tmp_path / ".octa",
        rag_backend="memory",
        qdrant_url="http://127.0.0.1:6335",
        qdrant_collection="knowledge_chunks_dev",
        knowledge_globs=("**/*.md",),
    )


def test_fixture_mail_items_default(tmp_path) -> None:
    config = _config(tmp_path)
    items = fixture_mail_items(config)
    assert len(items) >= 1
    assert items[0].sender
    assert items[0].subject


def test_fixture_mail_items_from_file(tmp_path) -> None:
    config = _config(tmp_path)
    path = config.octa_state_dir / "mail-fixture.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        '[{"sender": "ceo@example.com", "subject": "Board prep", "received_at": "2026-06-15T08:00:00"}]',
        encoding="utf-8",
    )
    items = fixture_mail_items(config)
    assert len(items) == 1
    assert items[0].subject == "Board prep"
    assert items[0].source == "fixture-file"


@pytest.mark.asyncio
async def test_list_unread_summary_returns_fixture(tmp_path) -> None:
    config = _config(tmp_path)
    items, source = await list_unread_summary(config)
    assert items
    assert source in {"fixture", "fixture-file"}
