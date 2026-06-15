import json
from pathlib import Path

import pytest

from secure_agentic_ai.infrastructure.macos.calendar_provider import (
    fixture_events,
    list_today_calendar_events,
    load_cached_events,
    save_cached_events,
)
from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig


def _config(tmp_path: Path, **overrides: object) -> WorkspaceConfig:
    base = {
        "enabled": True,
        "knowledge_root": tmp_path / "knowledge",
        "ledger_path": tmp_path / "ledger.sqlite",
        "journal_dir": tmp_path / "journal",
        "llm_provider": "dry",
        "deepseek_model": "deepseek-v4-flash",
        "deepseek_base_url": "https://api.deepseek.com",
        "deepseek_bw_label": "",
        "minimax_model": "MiniMax-M3",
        "minimax_base_url": "https://api.minimax.io/v1",
        "minimax_bw_label": "",
        "calendar_provider": "fixture",
        "calendar_fixture_path": tmp_path / "calendar-fixture.json",
        "calendar_include": (),
        "calendar_exclude": (),
        "octa_state_dir": tmp_path / ".octa",
        "rag_backend": "memory",
        "qdrant_url": "http://127.0.0.1:6335",
        "qdrant_collection": "knowledge_chunks_dev",
        "knowledge_globs": ("**/*.md",),
    }
    base.update(overrides)
    return WorkspaceConfig(**base)


def test_fixture_events_from_file(tmp_path: Path) -> None:
    config = _config(tmp_path)
    config.calendar_fixture_path.write_text(
        json.dumps([{"time": "10:00", "title": "Spotkanie z klientem", "calendar": "Praca"}]),
        encoding="utf-8",
    )
    events = fixture_events(config)
    assert len(events) == 1
    assert events[0].title == "Spotkanie z klientem"
    assert events[0].source == "fixture-file"


@pytest.mark.asyncio
async def test_list_today_calendar_fixture_mode(tmp_path: Path) -> None:
    config = _config(tmp_path)
    events, source = await list_today_calendar_events(config)
    assert source == "fixture"
    assert len(events) >= 3


@pytest.mark.asyncio
async def test_list_today_calendar_cache_mode(tmp_path: Path) -> None:
    from datetime import date

    from secure_agentic_ai.application.calendar import CalendarEventItem

    config = _config(tmp_path, calendar_provider="cache")
    day = date.today().isoformat()
    save_cached_events(
        config,
        day,
        [CalendarEventItem(time="11:00", title="Sync", calendar="Dom", source="macos")],
        source="macos",
    )
    events, source = await list_today_calendar_events(config)
    assert source == "cache"
    assert events[0].title == "Sync"


@pytest.mark.asyncio
async def test_list_today_calendar_cache_mode_empty_falls_back_fixture(tmp_path: Path) -> None:
    config = _config(tmp_path, calendar_provider="cache")
    events, source = await list_today_calendar_events(config)
    assert source == "fixture"
    assert len(events) >= 1


def test_calendar_cache_roundtrip(tmp_path: Path) -> None:
    from secure_agentic_ai.application.calendar import CalendarEventItem

    config = _config(tmp_path)
    day = "2026-06-14"
    save_cached_events(
        config,
        day,
        [CalendarEventItem(time="09:00", title="Deep work", calendar="Dom", source="macos")],
        source="macos",
    )
    cached = load_cached_events(config, day)
    assert cached is not None
    assert cached[0].title == "Deep work"
