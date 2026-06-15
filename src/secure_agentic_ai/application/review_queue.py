from dataclasses import dataclass

from secure_agentic_ai.application.chat_reply import ChatReply


@dataclass(frozen=True)
class PendingReviewItem:
    request_id: str
    description: str
    actor_display_name: str
    risk_level: str
    action_type: str


def matches_review_query(message: str) -> bool:
    lowered = message.lower()
    return any(
        word in lowered
        for word in (
            "review",
            "akcept",
            "approve",
            "hitl",
            "zatwierdz",
            "odrzuć",
            "odrzuc",
            "kolejk",
        )
    )


def matches_attention_query(message: str) -> bool:
    lowered = message.lower()
    return any(
        phrase in lowered
        for phrase in (
            "wymaga uwagi",
            "co czeka",
            "co pending",
            "co mam",
            "status dnia",
            "podsumowanie",
            "overview",
            "attention",
            "pending",
        )
    )


def format_review_reply(items: tuple[PendingReviewItem, ...]) -> ChatReply:
    if not items:
        return ChatReply(
            message="Kolejka `#Review` jest pusta — brak akcji do zatwierdzenia.",
            suggested_hash="#Review",
        )
    lines = [f"- **{item.description}** ({item.risk_level}) — {item.actor_display_name}" for item in items]
    count = len(items)
    noun = "akcja" if count == 1 else "akcje" if 2 <= count <= 4 else "akcji"
    header = f"W kolejce `#Review` czeka **{count}** {noun}:\n\n"
    return ChatReply(
        message=header + "\n".join(lines) + "\n\n→ `#Review`",
        suggested_hash="#Review",
    )


def format_attention_reply(
    pending: tuple[PendingReviewItem, ...],
    *,
    blocked_count: int,
    blocked_titles: tuple[str, ...],
) -> ChatReply:
    sections: list[str] = []

    if pending:
        review_lines = [f"- {item.description} ({item.risk_level})" for item in pending[:5]]
        suffix = f"\n- … i {len(pending) - 5} więcej" if len(pending) > 5 else ""
        sections.append(f"**Review ({len(pending)})** — wymaga zatwierdzenia CEO:\n" + "\n".join(review_lines) + suffix)
    else:
        sections.append("**Review** — kolejka pusta.")

    if blocked_count:
        blocked_lines = "\n".join(f"- {title}" for title in blocked_titles[:5])
        suffix = f"\n- … i {blocked_count - 5} więcej" if blocked_count > 5 else ""
        sections.append(f"**Board ({blocked_count} zablokowanych)**:\n{blocked_lines}{suffix}")
    else:
        sections.append("**Board** — brak zablokowanych zadań.")

    suggested = "#Review" if pending else "#Board" if blocked_count else "#Planning"
    return ChatReply(
        message="Co wymaga uwagi:\n\n" + "\n\n".join(sections) + f"\n\n→ `{suggested}`",
        suggested_hash=suggested,
    )
