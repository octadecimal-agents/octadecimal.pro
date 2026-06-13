from pipecat.frames.frames import Frame, TranscriptionFrame
from pipecat.processors.frame_processor import FrameProcessor, FrameDirection

from pipecat_translator.rag.store import VectorStore


class RAGProcessor(FrameProcessor):
    def __init__(self, store: VectorStore):
        super().__init__()
        self._store = store
        self.last_context: str = ""

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if isinstance(frame, TranscriptionFrame) and self._store.ready:
            results = self._store.search(frame.text, top_k=3)
            if results:
                lines = [f"- {r.text} (temat: {r.topic})" for r in results]
                self.last_context = "\n".join(lines)
