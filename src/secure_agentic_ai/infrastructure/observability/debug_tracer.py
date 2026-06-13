import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from uuid import uuid4


class DebugTracer:
    def __init__(self, trace_id: str | None = None) -> None:
        self._trace_id = trace_id or str(uuid4())

    @property
    def trace_id(self) -> str:
        return self._trace_id

    @asynccontextmanager
    async def span(self, name: str, attributes: dict[str, str] | None = None) -> AsyncGenerator[None]:
        attrs = attributes or {}
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = (time.perf_counter() - start) * 1000
            attrs_str = " ".join(f"{k}={v}" for k, v in attrs.items())
            print(f"[trace:{self._trace_id}] span={name} duration_ms={elapsed:.1f} {attrs_str}")
