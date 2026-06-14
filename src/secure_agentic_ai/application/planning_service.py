from datetime import date

from secure_agentic_ai.application.calendar import CalendarEventItem
from secure_agentic_ai.infrastructure.workspace.ledger import PlanItem, WorkspaceLedger

DEFAULT_CALENDAR = (
    ("09:00", "Sprint planning wewnętrzny"),
    ("13:30", "Review HITL — akceptacje CEO"),
    ("17:00", "Retro dnia + journal"),
)


def generate_daily_plan(
    ledger: WorkspaceLedger,
    plan_date: str | None = None,
    calendar_events: list[CalendarEventItem] | None = None,
) -> list[PlanItem]:
    day = plan_date or date.today().isoformat()
    items: list[tuple[str, str]] = []

    events = calendar_events
    if not events:
        events = [CalendarEventItem(time=time, title=title, source="fixture") for time, title in DEFAULT_CALENDAR]

    for event in events:
        label = event.title if event.time in {"", "all-day"} else f"{event.time} — {event.title}"
        items.append((label, "calendar"))

    for task in ledger.list_tasks(status="doing")[:2]:
        items.append((f"[{task.team}] {task.title}", "board"))

    for task in ledger.list_tasks(status="blocked")[:2]:
        items.append((f"Odblokować: {task.title} ({task.team})", "board"))

    items.extend(
        [
            ("Deep work — Octa OS / Cursor", "ao"),
            ("Przegląd `#Review` i akceptacje", "ao"),
        ]
    )

    return ledger.replace_plan_items(day, items)
