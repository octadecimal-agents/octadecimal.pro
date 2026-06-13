from dataclasses import dataclass, field
from uuid import uuid4


@dataclass(frozen=True)
class ChunkMetadata:
    source: str
    page: int | None = None
    section: str | None = None
    document_id: str = ""


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str = field(default_factory=lambda: str(uuid4()))
    document_id: str = ""
    text: str = ""
    metadata: ChunkMetadata | None = None


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: DocumentChunk
    score: float
