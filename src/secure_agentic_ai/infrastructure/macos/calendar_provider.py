import asyncio
import json
import platform
from datetime import date
from pathlib import Path

from secure_agentic_ai.application.calendar import CalendarEventItem
from secure_agentic_ai.application.planning_service import DEFAULT_CALENDAR
from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig

CACHE_FILENAME = "calendar-cache.json"


def fixture_events(config: WorkspaceConfig) -> list[CalendarEventItem]:
    path = config.calendar_fixture_path
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = None
        if isinstance(data, list):
            parsed = [_event_from_mapping(item, source="fixture-file") for item in data if isinstance(item, dict)]
            if parsed:
                return parsed

    return [
        CalendarEventItem(time=time, title=title, source="fixture")
        for time, title in DEFAULT_CALENDAR
    ]


def _event_from_mapping(item: dict[str, object], *, source: str) -> CalendarEventItem:
    time = str(item.get("time", "00:00"))
    title = str(item.get("title", "")).strip()
    calendar = item.get("calendar")
    return CalendarEventItem(
        time=time,
        title=title,
        calendar=str(calendar) if calendar else None,
        source=source,
    )


def _cache_path(config: WorkspaceConfig) -> Path:
    return config.octa_state_dir / CACHE_FILENAME


def load_cached_events(config: WorkspaceConfig, day: str) -> list[CalendarEventItem] | None:
    path = _cache_path(config)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict) or data.get("date") != day:
        return None
    events = data.get("events")
    if not isinstance(events, list):
        return None
    parsed = [_event_from_mapping(item, source=str(data.get("source", "cache"))) for item in events if isinstance(item, dict)]
    return parsed or None


def save_cached_events(config: WorkspaceConfig, day: str, events: list[CalendarEventItem], *, source: str) -> None:
    path = _cache_path(config)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "date": day,
        "source": source,
        "events": [
            {
                "time": event.time,
                "title": event.title,
                "calendar": event.calendar,
            }
            for event in events
        ],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _fetch_macos_events_sync(config: WorkspaceConfig, day: str) -> list[CalendarEventItem]:
    if platform.system() != "Darwin":
        raise RuntimeError("EventKit calendar is only available on macOS")

    from calctl.calendar import list_events

    events = list_events(
        from_date=day,
        to_date=day,
        calendars=list(config.calendar_include) or None,
        exclude_calendars=list(config.calendar_exclude) or None,
    )
    parsed: list[CalendarEventItem] = []
    for item in events:
        start = str(item.get("start", ""))
        time = start[11:16] if len(start) >= 16 else "00:00"
        if item.get("all_day"):
            time = "all-day"
        parsed.append(
            CalendarEventItem(
                time=time,
                title=str(item.get("title", "")).strip(),
                calendar=str(item.get("calendar", "")) or None,
                source="macos",
            )
        )
    parsed.sort(key=lambda event: event.time)
    return parsed


async def list_today_calendar_events(config: WorkspaceConfig) -> tuple[list[CalendarEventItem], str]:
    day = date.today().isoformat()
    provider = config.calendar_provider

    if provider == "fixture":
        events = fixture_events(config)
        return events, events[0].source if events else "fixture"

    if provider in {"macos", "auto"}:
        try:
            events = await asyncio.to_thread(_fetch_macos_events_sync, config, day)
            if events:
                save_cached_events(config, day, events, source="macos")
            return events, "macos"
        except Exception as exc:
            denied = type(exc).__name__ == "AccessDeniedError"
            if denied or provider == "macos":
                cached = load_cached_events(config, day)
                if cached:
                    return cached, "cache"
                events = fixture_events(config)
                suffix = "denied" if denied else "error"
                return events, f"fixture-{suffix}"

    if provider == "auto":
        cached = load_cached_events(config, day)
        if cached:
            return cached, "cache"

    events = fixture_events(config)
    return events, "fixture"
