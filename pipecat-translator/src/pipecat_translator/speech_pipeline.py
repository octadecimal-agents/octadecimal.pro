import json

from loguru import logger

from pipecat.frames.frames import (
    Frame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    LLMTextFrame,
    LLMContextFrame,
    TranscriptionFrame,
)
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.frame_processor import FrameProcessor, FrameDirection

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


class ContextInjector(FrameProcessor):
    def __init__(
        self,
        source_lang: str = "pl",
        target_lang: str = "en",
        rag_context_provider=None,
    ):
        super().__init__()
        self._source_lang = source_lang
        self._target_lang = target_lang
        self._rag_provider = rag_context_provider
        self._base_prompt = TRANSLATION_SYSTEM_PROMPT.format(
            source_lang=source_lang,
            target_lang=target_lang,
        )
        self.context = LLMContext(messages=[
            {"role": "system", "content": self._base_prompt},
        ])

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, TranscriptionFrame):
            text = frame.text
            if not text.strip():
                return

            rag_context = ""
            if self._rag_provider:
                rag_context = self._rag_provider()

            if rag_context:
                user_content = f"{text}\n\nPrzydatne zwroty:\n{rag_context}"
            else:
                user_content = text

            logger.info(f"[{self._source_lang.upper()}] Rozpoznano: {text}")
            self.context.add_message({"role": "user", "content": user_content})
            await self.push_frame(LLMContextFrame(context=self.context))


class ResponseHandler(FrameProcessor):
    def __init__(self, context: LLMContext, target_lang: str = "en"):
        super().__init__()
        self._context = context
        self._target_lang = target_lang
        self._buffer = ""

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, LLMFullResponseStartFrame):
            self._buffer = ""
        elif isinstance(frame, LLMTextFrame):
            self._buffer += frame.text
        elif isinstance(frame, LLMFullResponseEndFrame):
            if not self._buffer:
                return
            self._context.add_message({"role": "assistant", "content": self._buffer})
            try:
                data = json.loads(self._buffer)
                translation = data.get("translation", self._buffer)
                suggestion = data.get("suggestion", "")
                logger.info(f"[{self._target_lang.upper()}] Tłumaczenie: {translation}")
                if suggestion:
                    logger.info(f"[💡] Sugestia: {suggestion}")
            except json.JSONDecodeError:
                logger.info(f"[{self._target_lang.upper()}] {self._buffer}")
            self._buffer = ""
