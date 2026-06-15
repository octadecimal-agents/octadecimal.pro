import pytest

from secure_agentic_ai.infrastructure.llm.factory import resolve_chat_provider
from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig


def _config(tmp_path, llm_provider: str) -> WorkspaceConfig:
    root = tmp_path / "knowledge"
    root.mkdir()
    return WorkspaceConfig(
        enabled=True,
        knowledge_root=root,
        ledger_path=tmp_path / "ledger.sqlite",
        journal_dir=root / "journal",
        llm_provider=llm_provider,
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


@pytest.mark.asyncio
async def test_resolve_chat_provider_dry_by_default(tmp_path) -> None:
    resolved = await resolve_chat_provider(_config(tmp_path, "dry"))
    assert resolved.active == "dry"
    assert resolved.fallback_reason is None
    assert resolved.provider.is_available() is False


@pytest.mark.asyncio
async def test_minimax_without_token_falls_back_to_dry(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MINIMAX_API_TOKEN", raising=False)
    monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
    monkeypatch.delenv("BWS_ACCESS_TOKEN", raising=False)
    resolved = await resolve_chat_provider(_config(tmp_path, "minimax"))
    assert resolved.active == "dry"
    assert resolved.fallback_reason is not None
    assert "MINIMAX" in resolved.fallback_reason
