"""Seed Octa Workspace MVP: plan items for today."""

from datetime import date

from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig
from secure_agentic_ai.infrastructure.workspace.ledger import WorkspaceLedger


def seed_plan() -> None:
    config = WorkspaceConfig.from_env()
    ledger = WorkspaceLedger(config.ledger_path)
    today = date.today().isoformat()
    if ledger.list_plan_items(today):
        print(f"  Plan for {today} already exists — skip")
        return
    items = [
        ("Review Workspace MVP checklist", "ao"),
        ("Automation: embed-knowledge phase 0", "ao"),
        ("Security: policy.yaml tier review", "ao"),
        ("Deep work block — Cursor / Octa OS", "calendar"),
    ]
    ledger.replace_plan_items(today, items)
    print(f"  Created plan with {len(items)} items for {today}")


if __name__ == "__main__":
    print("Seeding workspace plan...")
    seed_plan()
    print("Done.")
