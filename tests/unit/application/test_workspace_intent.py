import pytest

from secure_agentic_ai.application.workspace_intent import ChatIntent, classify_chat_intent


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("Co wymaga uwagi?", ChatIntent.ATTENTION),
        ("Co czeka w review?", ChatIntent.REVIEW),
        ("Co jest zablokowane?", ChatIntent.BLOCKED),
        ("wygeneruj plan", ChatIntent.GENERATE_PLAN),
        ("Jaki plan na dziś?", ChatIntent.PLAN_TODAY),
        ("jak backup Qdrant?", ChatIntent.KNOWLEDGE),
    ],
)
def test_classify_chat_intent(message: str, expected: ChatIntent) -> None:
    assert classify_chat_intent(message) is expected
