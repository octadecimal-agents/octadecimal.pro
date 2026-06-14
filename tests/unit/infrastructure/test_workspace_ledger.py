import pytest

from secure_agentic_ai.infrastructure.workspace.ledger import WorkspaceLedger


@pytest.fixture
def ledger(tmp_path):
    return WorkspaceLedger(tmp_path / "ledger.sqlite")


def test_create_and_list_tasks(ledger: WorkspaceLedger) -> None:
    task = ledger.create_task("automation", "Build embed pipeline", intent="MVP ingest")
    tasks = ledger.list_tasks(team="automation")
    assert len(tasks) == 1
    assert tasks[0].id == task.id
    assert tasks[0].title == "Build embed pipeline"


def test_update_task_status(ledger: WorkspaceLedger) -> None:
    task = ledger.create_task("security", "Audit MCP")
    updated = ledger.update_task_status(task.id, "blocked")
    assert updated is not None
    assert updated.status == "blocked"
    blocked = ledger.list_tasks(status="blocked")
    assert len(blocked) == 1


def test_invalid_team_raises(ledger: WorkspaceLedger) -> None:
    with pytest.raises(ValueError, match="Invalid team"):
        ledger.create_task("unknown", "Bad task")


def test_plan_items_replace(ledger: WorkspaceLedger) -> None:
    items = ledger.replace_plan_items(
        "2026-06-14",
        [("Morning planning", "ao"), ("Deep work", "ceo")],
    )
    assert len(items) == 2
    assert items[0].title == "Morning planning"
    reloaded = ledger.list_plan_items("2026-06-14")
    assert len(reloaded) == 2


def test_seed_demo_tasks_idempotent(ledger: WorkspaceLedger) -> None:
    ledger.seed_demo_tasks()
    first_count = len(ledger.list_tasks())
    ledger.seed_demo_tasks()
    assert len(ledger.list_tasks()) == first_count
    assert first_count == 3
