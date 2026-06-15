from secure_agentic_ai.application.planning_service import generate_daily_plan
from secure_agentic_ai.infrastructure.workspace.ledger import WorkspaceLedger


def test_generate_daily_plan(tmp_path) -> None:
    ledger = WorkspaceLedger(tmp_path / "ledger.sqlite")
    ledger.create_task("knowledge", "Embed pipeline", status="doing")
    items = generate_daily_plan(ledger, plan_date="2026-06-14")
    assert len(items) >= 5
    assert any("Sprint planning" in item.title for item in items)
    assert any("Embed pipeline" in item.title for item in items)
    reloaded = ledger.list_plan_items("2026-06-14")
    assert len(reloaded) == len(items)
