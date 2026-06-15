import pytest

from secure_agentic_ai.infrastructure.llm.chat_prompts import (
    build_rag_messages,
    parse_suggested_hash,
    sanitize_llm_reply,
)


def test_build_rag_messages_includes_context() -> None:
    messages = build_rag_messages(
        "jak backup Qdrant?",
        [("02-6-Rooms-Model/Operacje/serwer/Backup.md", "Qdrant snapshot daily")],
    )
    assert messages[0]["role"] == "system"
    assert "Backup.md" in messages[1]["content"]
    assert "jak backup Qdrant?" in messages[1]["content"]


def test_parse_suggested_hash() -> None:
    assert parse_suggested_hash("Sprawdź szczegóły w #Wiki.") == "#Wiki"
    assert parse_suggested_hash("→ `#Planning`") == "#Planning"
    assert parse_suggested_hash("brak tagu") is None


def test_sanitize_llm_reply_strips_minimax_thinking() -> None:
    raw = "<think>\nThe user asked about backup.\n</think>\n\n# Backup Qdrant\n\n→ `#Wiki`"
    cleaned = sanitize_llm_reply(raw)
    assert "redacted_thinking" not in cleaned
    assert cleaned.startswith("# Backup Qdrant")
    assert parse_suggested_hash(cleaned) == "#Wiki"


def test_sanitize_llm_reply_strips_think_tag() -> None:
    tag = "think"
    raw = f"<{tag}>internal chain of thought</{tag}>\nTak, MiniMax działa."
    assert sanitize_llm_reply(raw) == "Tak, MiniMax działa."


@pytest.mark.asyncio
async def test_deepseek_complete(monkeypatch: pytest.MonkeyPatch) -> None:
    from secure_agentic_ai.infrastructure.llm.deepseek_provider import DeepSeekChatProvider

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {"choices": [{"message": {"content": "Odpowiedź AO → `#Wiki`"}}]}

    class FakeClient:
        async def __aenter__(self) -> "FakeClient":
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def post(self, *args: object, **kwargs: object) -> FakeResponse:
            return FakeResponse()

    monkeypatch.setattr(
        "secure_agentic_ai.infrastructure.llm.openai_compat_provider.httpx.AsyncClient",
        lambda **kwargs: FakeClient(),
    )

    provider = DeepSeekChatProvider("test-key")
    text = await provider.complete([{"role": "user", "content": "cześć"}])
    assert "Odpowiedź AO" in text
    assert provider.label == "deepseek:deepseek-v4-flash"


@pytest.mark.asyncio
async def test_minimax_complete(monkeypatch: pytest.MonkeyPatch) -> None:
    from secure_agentic_ai.infrastructure.llm.minimax_provider import MiniMaxChatProvider

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {"choices": [{"message": {"content": "MiniMax AO → `#Board`"}}]}

    class FakeClient:
        async def __aenter__(self) -> "FakeClient":
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def post(self, url: str, *args: object, **kwargs: object) -> FakeResponse:
            assert url == "https://api.minimax.io/v1/chat/completions"
            return FakeResponse()

    monkeypatch.setattr(
        "secure_agentic_ai.infrastructure.llm.openai_compat_provider.httpx.AsyncClient",
        lambda **kwargs: FakeClient(),
    )

    provider = MiniMaxChatProvider("test-token")
    text = await provider.complete([{"role": "user", "content": "cześć"}])
    assert "MiniMax AO" in text
    assert provider.label == "minimax:MiniMax-M3"
