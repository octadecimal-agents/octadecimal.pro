import json
import re

from loguru import logger

from pipecat.frames.frames import (
    Frame,
    LLMFullResponseEndFrame,
    LLMTextFrame,
)
from pipecat.processors.frame_processor import FrameProcessor, FrameDirection


class SuggestionProcessor(FrameProcessor):
    """Tap processor that extracts response suggestions from LLM output.

    Passes all frames through unchanged, and accumulates LLM text to
    detect the "suggestion" field in JSON-formatted translations.
    """

    def __init__(self, source_lang: str = "pl", target_lang: str = "en"):
        super().__init__()
        self._source_lang = source_lang
        self._target_lang = target_lang
        self._buffer = ""

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        if isinstance(frame, LLMTextFrame):
            self._buffer += frame.text
        elif isinstance(frame, LLMFullResponseEndFrame):
            suggestion = self._extract_suggestion(self._buffer)
            self._buffer = ""
            if suggestion:
                logger.info(f"Suggestion: {suggestion}")

        await self.push_frame(frame, direction)

    def _extract_suggestion(self, text: str) -> str | None:
        try:
            data = json.loads(text)
            return data.get("suggestion")
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

        match = re.search(r'"suggestion"\s*:\s*"([^"]+)"', text)
        if match:
            return match.group(1)

        return None
