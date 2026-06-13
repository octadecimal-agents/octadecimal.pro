import asyncio
import json
import os

from dotenv import load_dotenv
from loguru import logger

from pipecat.frames.frames import (
    Frame,
    LLMContextFrame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    LLMTextFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineWorker
from pipecat.processors.frame_processor import FrameProcessor, FrameDirection
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.workers.runner import WorkerRunner

from pipecat_translator.suggestion_processor import SuggestionProcessor

load_dotenv()

TRANSLATION_SYSTEM_PROMPT = """Jesteś asystentem dwujęzycznej rozmowy PL↔EN.
Język źródłowy: {source_lang}
Język docelowy: {target_lang}

Twój cel:
1. Przetłumacz każdą wypowiedź na język docelowy
2. Zaproponuj 1-2 zdania odpowiedzi w języku źródłowym

Format odpowiedzi (tylko JSON, bez dodatkowego tekstu):
{{
  "translation": "przetłumaczony tekst",
  "suggestion": "sugerowana odpowiedź w języku źródłowym"
}}

Temat rozmowy: ogólny
Język źródłowy: {source_lang}
Język docelowy: {target_lang}
"""


class LLMResponseCollector(FrameProcessor):
    """Collects LLM text frames and fires a callback on full response."""

    def __init__(self, on_response: callable):
        super().__init__()
        self._on_response = on_response
        self._buffer = ""

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        await self.push_frame(frame, direction)

        if isinstance(frame, LLMFullResponseStartFrame):
            self._buffer = ""
        elif isinstance(frame, LLMTextFrame):
            self._buffer += frame.text
        elif isinstance(frame, LLMFullResponseEndFrame):
            text = self._buffer
            self._buffer = ""
            if text and self._on_response:
                await self._on_response(text)


def create_translation_context(
    source_lang: str = "pl",
    target_lang: str = "en",
) -> LLMContext:
    messages = [
        {
            "role": "system",
            "content": TRANSLATION_SYSTEM_PROMPT.format(
                source_lang=source_lang,
                target_lang=target_lang,
            ),
        },
    ]
    return LLMContext(messages=messages)


def build_translation_pipeline(
    source_lang: str = "pl",
    target_lang: str = "en",
    on_response: callable = None,
) -> Pipeline:
    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        settings=OpenAILLMService.Settings(
            model=os.getenv("LLM_MODEL", "gpt-4o"),
        ),
    )

    suggestion_processor = SuggestionProcessor(
        source_lang=source_lang,
        target_lang=target_lang,
    )

    response_collector = LLMResponseCollector(on_response=on_response)

    pipeline = Pipeline([
        llm,
        suggestion_processor,
        response_collector,
    ])

    return pipeline


async def run_console_session(source_lang="pl", target_lang="en"):
    context = create_translation_context(source_lang, target_lang)
    context_lock = asyncio.Lock()

    async def on_response(text: str):
        try:
            data = json.loads(text)
            print(f"\n  [{target_lang.upper()}] Tłumaczenie: {data.get('translation', '—')}")
            print(f"  [💡] Sugestia:      {data.get('suggestion', '—')}\n")
            async with context_lock:
                context.add_message({"role": "assistant", "content": text})
        except json.JSONDecodeError:
            print(f"\n  [{target_lang.upper()}] {text}\n")
            async with context_lock:
                context.add_message({"role": "assistant", "content": text})

    pipeline = build_translation_pipeline(
        source_lang=source_lang,
        target_lang=target_lang,
        on_response=on_response,
    )

    worker = PipelineWorker(
        pipeline=pipeline,
        name="translation-worker",
    )

    runner = WorkerRunner()
    await runner.add_workers(worker)

    runner_task = asyncio.create_task(runner.run())
    await asyncio.sleep(0.5)

    lang_map = {"pl": "polski", "en": "angielski"}
    print(f"\n{'='*60}")
    print(f"  Pipecat Translator — Phase 1: Console Pipeline")
    print(f"  {lang_map[source_lang]} ↔ {lang_map[target_lang]}")
    print(f"{'='*60}")
    print("\nWpisz tekst do przetłumaczenia (lub 'exit' aby zakończyć):\n")

    try:
        loop = asyncio.get_running_loop()
        while True:
            text = await loop.run_in_executor(None, lambda: input(f"[{source_lang.upper()}] > ").strip())
            if not text:
                continue
            if text.lower() in ("exit", "quit", "q", "koniec"):
                break

            async with context_lock:
                context.add_message({"role": "user", "content": text})

            await worker.queue_frame(LLMContextFrame(context=context))

            # Give pipeline time to process before next prompt appears
            await asyncio.sleep(0.5)

    except (EOFError, KeyboardInterrupt):
        pass
    finally:
        print("\nDo widzenia!")
        await runner.end()
        runner_task.cancel()
        try:
            await runner_task
        except (asyncio.CancelledError):
            pass
