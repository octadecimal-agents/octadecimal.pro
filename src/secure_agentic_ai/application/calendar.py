from dataclasses import dataclass


@dataclass(frozen=True)
class CalendarEventItem:
    time: str
    title: str
    calendar: str | None = None
    source: str = "fixture"
