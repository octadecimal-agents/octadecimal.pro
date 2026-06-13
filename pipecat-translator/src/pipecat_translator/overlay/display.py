import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from enum import Enum, auto

from rich.align import Align
from rich.console import Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class EventKind(Enum):
    TRANSCRIPTION = auto()
    TRANSLATION = auto()
    SUGGESTION = auto()
    STATUS = auto()


@dataclass
class OverlayEvent:
    kind: EventKind
    text: str
    lang: str = ""
    detail: str = ""


class TranslationOverlay:
    def __init__(self, source_lang: str = "PL", target_lang: str = "EN"):
        self._source_lang = source_lang
        self._target_lang = target_lang
        self._queue: asyncio.Queue[OverlayEvent] = asyncio.Queue()
        self._rows: list[tuple[str, str, str]] = []
        self._status = "Nasłuchiwanie..."
        self._max_rows = 12

    async def push(self, event: OverlayEvent) -> None:
        await self._queue.put(event)

    def _process_event(self, event: OverlayEvent) -> None:
        if event.kind == EventKind.TRANSCRIPTION:
            self._rows.append((f"[{event.lang}] 🎤", event.text, "cyan"))
            self._status = "Mówi..."
        elif event.kind == EventKind.TRANSLATION:
            self._rows.append((f"[{event.lang}] 🔈", event.text, "green"))
            self._status = "Odtwarzanie..."
        elif event.kind == EventKind.SUGGESTION:
            self._rows.append(("💡 Sugestia", f"{event.text}", "yellow"))
        elif event.kind == EventKind.STATUS:
            self._status = event.text
            if event.detail:
                self._rows.append(("ℹ️", event.detail, "white"))

        if len(self._rows) > self._max_rows:
            self._rows = self._rows[-self._max_rows:]

    def _build_layout(self) -> Panel:
        title = Text(f"Pipecat Translator  —  {self._source_lang} ↔ {self._target_lang}")
        title.stylize("bold cyan")

        status_panel = Panel(
            Align.center(Text(self._status, style="bold yellow")),
            border_style="green",
        )

        table = Table(show_header=True, header_style="bold magenta", box=None, padding=(0, 1))
        table.add_column("", width=14, no_wrap=True)
        table.add_column("Treść", ratio=1)

        for label, text, color in self._rows:
            table.add_row(
                Text(label, style=color),
                Text(text, style=color, no_wrap=False, overflow="fold"),
            )

        body = Group(status_panel, Panel(table, border_style="blue"))

        return Panel(
            body,
            title=title,
            border_style="cyan",
            padding=(1, 2),
        )

    async def run(self) -> None:
        async with Live(
            self._build_layout(),
            auto_refresh=False,
            screen=True,
        ) as live:
            while True:
                try:
                    event = await asyncio.wait_for(self._queue.get(), timeout=0.2)
                    self._process_event(event)
                except asyncio.TimeoutError:
                    pass
                live.update(self._build_layout())
