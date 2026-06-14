import pytest

from secure_agentic_ai.infrastructure.llm.deepseek_provider import (
    build_rag_messages,
    parse_suggested_hash,
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
        "secure_agentic_ai.infrastructure.llm.deepseek_provider.httpx.AsyncClient",
        lambda **kwargs: FakeClient(),
    )

    provider = DeepSeekChatProvider("test-key")
    text = await provider.complete([{"role": "user", "content": "cześć"}])
    assert "Odpowiedź AO" in text
    assert provider.label == "deepseek:deepseek-v4-flash"
