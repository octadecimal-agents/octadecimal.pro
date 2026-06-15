from pathlib import Path

import pytest

from secure_agentic_ai.infrastructure.llm.secret_resolver import (
    resolve_deepseek_api_key,
    resolve_minimax_api_token,
)


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
async def test_resolve_deepseek_returns_none_without_sources(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("BWS_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("BW_SECRET_ID_DEEPSEEK_API_KEY", raising=False)
    key = await resolve_deepseek_api_key(knowledge_root=tmp_path, bw_label="missing/label")
    assert key is None


@pytest.mark.asyncio
async def test_resolve_minimax_prefers_token_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MINIMAX_API_TOKEN", "token-from-env")
    token = await resolve_minimax_api_token(knowledge_root=tmp_path, bw_label="")
    assert token == "token-from-env"


@pytest.mark.asyncio
async def test_resolve_minimax_falls_back_to_api_key_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("MINIMAX_API_TOKEN", raising=False)
    monkeypatch.setenv("MINIMAX_API_KEY", "key-alias")
    token = await resolve_minimax_api_token(knowledge_root=tmp_path, bw_label="")
    assert token == "key-alias"


@pytest.mark.asyncio
async def test_resolve_minimax_from_bsm(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("MINIMAX_API_TOKEN", raising=False)
    monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
    monkeypatch.setenv("BWS_ACCESS_TOKEN", "test-token")

    async def fake_bsm(**kwargs: object) -> str:
        return "token-from-bsm"

    monkeypatch.setattr(
        "secure_agentic_ai.infrastructure.llm.secret_resolver._resolve_from_bsm",
        fake_bsm,
    )
    token = await resolve_minimax_api_token(knowledge_root=tmp_path, bw_label="")
    assert token == "token-from-bsm"
