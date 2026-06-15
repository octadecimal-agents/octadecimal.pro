import json
import logging
from pathlib import Path

import pytest

from secure_agentic_ai.application.review_queue import PendingReviewItem
from secure_agentic_ai.application.workspace_tool_trace import log_tool_trace
from secure_agentic_ai.application.workspace_tools import (
    approvals_pending,
    board_list,
    plan_today,
)
from secure_agentic_ai.infrastructure.workspace.ledger import WorkspaceLedger


def test_approvals_pending_tool_summary() -> None:
    pending = (
        PendingReviewItem(
            request_id="demo-1",
            description="Deploy to staging",
            actor_display_name="Deploy Agent",
            risk_level="high",
            action_type="run_command",
        ),
    )
    result = approvals_pending(pending)
    assert result.row_count == 1
    assert "Deploy to staging" in result.summary


def test_board_list_tool(tmp_path: Path) -> None:
    ledger = WorkspaceLedger(tmp_path / "ledger.sqlite")
    ledger.create_task("automation", "Blocked item", status="blocked")
    result = board_list(ledger, status="blocked")
    assert result.row_count == 1
    assert "Blocked item" in result.summary


def test_plan_today_tool(tmp_path: Path) -> None:
    ledger = WorkspaceLedger(tmp_path / "ledger.sqlite")
    result = plan_today(ledger)
    assert result.row_count >= 0
    assert "Plan na dziś" in result.summary


def test_log_tool_trace_emits_json(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="secure_agentic_ai.workspace_agent")
    log_tool_trace(
        "test",
        [approvals_pending(())],
    )
    assert any('"event": "tool_trace"' in record.message for record in caplog.records)
    payload = json.loads(next(record.message for record in caplog.records if '"event": "tool_trace"' in record.message))
    assert payload["tools"][0]["name"] == "approvals_pending"
