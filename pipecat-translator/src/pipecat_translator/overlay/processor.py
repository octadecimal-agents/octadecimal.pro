from pipecat.frames.frames import (
    Frame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    LLMTextFrame,
    TranscriptionFrame,
)
from pipecat.processors.frame_processor import FrameProcessor, FrameDirection

from pipecat_translator.overlay.display import EventKind, OverlayEvent, TranslationOverlay


class OverlayProcessor(FrameProcessor):
    def __init__(self, overlay: TranslationOverlay, target_lang: str = "EN"):
        super().__init__()
        self._overlay = overlay
        self._target_lang = target_lang
        self._buffer = ""

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, TranscriptionFrame):
            await self._overlay.push(OverlayEvent(
                kind=EventKind.TRANSCRIPTION,
                text=frame.text,
                lang=self._target_lang if frame.text else "",
            ))
        elif isinstance(frame, LLMFullResponseStartFrame):
            self._buffer = ""
        elif isinstance(frame, LLMTextFrame):
            self._buffer += frame.text
        elif isinstance(frame, LLMFullResponseEndFrame):
            if self._buffer:
                import json
                try:
                    data = json.loads(self._buffer)
                    translation = data.get("translation", "")
                    suggestion = data.get("suggestion", "")
                    if translation:
                        await self._overlay.push(OverlayEvent(
                            kind=EventKind.TRANSLATION,
                            text=translation,
                            lang=self._target_lang,
                        ))
                    if suggestion:
                        await self._overlay.push(OverlayEvent(
                            kind=EventKind.SUGGESTION,
                            text=suggestion,
                        ))
                except json.JSONDecodeError:
                    await self._overlay.push(OverlayEvent(
                        kind=EventKind.TRANSLATION,
                        text=self._buffer,
                        lang=self._target_lang,
                    ))
                self._buffer = ""
