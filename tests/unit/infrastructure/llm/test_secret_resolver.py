from pathlib import Path

import pytest

from secure_agentic_ai.infrastructure.llm.secret_resolver import resolve_deepseek_api_key


@pytest.mark.asyncio
async def test_resolve_deepseek_prefers_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "env-key")
    key = await resolve_deepseek_api_key(knowledge_root=tmp_path, bw_label="")
    assert key == "env-key"


@pytest.mark.asyncio
async def test_resolve_deepseek_from_bsm(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setenv("BWS_ACCESS_TOKEN", "test-token")

    async def fake_bsm(**kwargs: object) -> str:
        return "sk-from-bsm"

    monkeypatch.setattr(
        "secure_agentic_ai.infrastructure.llm.secret_resolver._resolve_from_bsm",
        fake_bsm,
    )
    key = await resolve_deepseek_api_key(knowledge_root=tmp_path, bw_label="")
    assert key == "sk-from-bsm"


@pytest.mark.asyncio
async def test_resolve_deepseek_returns_none_without_sources(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("BWS_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("BW_SECRET_ID_DEEPSEEK_API_KEY", raising=False)
    key = await resolve_deepseek_api_key(knowledge_root=tmp_path, bw_label="missing/label")
    assert key is None
