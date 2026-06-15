from enum import StrEnum

from secure_agentic_ai.application.review_queue import matches_attention_query, matches_review_query


class ChatIntent(StrEnum):
    ATTENTION = "attention"
    REVIEW = "review"
    BLOCKED = "blocked"
    GENERATE_PLAN = "generate_plan"
    PLAN_TODAY = "plan_today"
    KNOWLEDGE = "knowledge"


def classify_chat_intent(message: str) -> ChatIntent:
    lowered = message.lower()

    if matches_review_query(message):
        return ChatIntent.REVIEW
    if matches_attention_query(message):
        return ChatIntent.ATTENTION
    if any(word in lowered for word in ("zablokow", "blocked", "blokad")):
        return ChatIntent.BLOCKED
    if "wygeneruj plan" in lowered or "generate plan" in lowered:
        return ChatIntent.GENERATE_PLAN
    if any(word in lowered for word in ("plan", "dzisiaj", "today", "planning")):
        return ChatIntent.PLAN_TODAY
    return ChatIntent.KNOWLEDGE
