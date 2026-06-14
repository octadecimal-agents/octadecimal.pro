from secure_agentic_ai.application.review_queue import (
    PendingReviewItem,
    format_attention_reply,
    format_review_reply,
    matches_attention_query,
    matches_review_query,
)


def _sample_items() -> tuple[PendingReviewItem, ...]:
    return (
        PendingReviewItem(
            request_id="demo-1",
            description="Deploy to staging",
            actor_display_name="Deploy Agent",
            risk_level="high",
            action_type="run_command",
        ),
        PendingReviewItem(
            request_id="demo-2",
            description="Write generated source file",
            actor_display_name="Dev Agent",
            risk_level="high",
            action_type="write_file",
        ),
    )


def test_matches_review_query() -> None:
    assert matches_review_query("Pokaż kolejkę review")
    assert matches_review_query("Co czeka na akceptację?")


def test_matches_attention_query() -> None:
    assert matches_attention_query("Co wymaga uwagi?")
    assert not matches_attention_query("jak backup Qdrant?")


def test_format_review_reply_lists_items() -> None:
    reply = format_review_reply(_sample_items())
    assert reply.suggested_hash == "#Review"
    assert "Deploy to staging" in reply.message
    assert "2" in reply.message


def test_format_review_reply_empty_queue() -> None:
    reply = format_review_reply(())
    assert "pusta" in reply.message.lower()


def test_format_attention_reply_prioritizes_review() -> None:
    reply = format_attention_reply(_sample_items(), blocked_count=1, blocked_titles=("Blocked task",))
    assert reply.suggested_hash == "#Review"
    assert "Review (2)" in reply.message
    assert "Blocked task" in reply.message
