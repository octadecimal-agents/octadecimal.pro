import re
from dataclasses import dataclass
from pathlib import Path

from secure_agentic_ai.application.use_cases import RetrieveContextUseCase
from secure_agentic_ai.domain.knowledge import RetrievalScoreBreakdown, RetrievedChunk
from secure_agentic_ai.infrastructure.workspace.knowledge_policy import RetrievalWeights

_TOKEN = re.compile(r"[a-z0-9\u0105-\u017c]{3,}", re.IGNORECASE)
_HEADING = re.compile(r"^#+\s+(.+)$", re.MULTILINE)


def _query_tokens(query: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(query)]


def keyword_score(query: str, source: str, text: str) -> float:
    """Path and filename token match (legacy name kept for tests)."""
    tokens = _query_tokens(query)
    if not tokens:
        return 0.0
    haystack = f"{source} {text}".lower()
    filename = source.rsplit("/", 1)[-1].lower().removesuffix(".md")
    score = 0.0
    for token in tokens:
        if token in haystack:
            score += 1.0
        if token == filename:
            score += 10.0
        elif token in filename:
            score += 2.0
    if "/.claude/" in source or ("/agents/" in source and "agent" in filename):
        score *= 0.85
    return score / len(tokens)


def heading_score(query: str, text: str) -> float:
    tokens = _query_tokens(query)
    headings = [heading.lower() for heading in _HEADING.findall(text)]
    if not tokens or not headings:
        return 0.0
    hits = 0
    for token in tokens:
        if any(token in heading for heading in headings):
            hits += 1
    return hits / len(tokens)


def recency_raw_score(source: str, knowledge_root: Path | None) -> float:
    if knowledge_root is None:
        return 0.0
    path = knowledge_root / source
    if not path.is_file():
        return 0.0
    return float(path.stat().st_mtime)


@dataclass(frozen=True)
class HybridKnowledgeSearch:
    """Vector search with weighted path, heading, and recency re-ranking."""

    retrieve: RetrieveContextUseCase
    weights: RetrievalWeights | None = None
    knowledge_root: Path | None = None

    def __post_init__(self) -> None:
        if self.weights is None:
            object.__setattr__(self, "weights", RetrievalWeights())

    async def search(self, query: str, k: int = 5) -> list[RetrievedChunk]:
        candidates = await self.retrieve.execute(query, k=max(k * 8, 100))
        tokens = _query_tokens(query)
        if tokens:
            title_hint = " ".join(token.capitalize() for token in tokens[:2])
            extra = await self.retrieve.execute(f"{title_hint} {query}", k=20)
            seen = {candidate.chunk.chunk_id for candidate in candidates}
            for item in extra:
                if item.chunk.chunk_id not in seen:
                    candidates.append(item)
                    seen.add(item.chunk.chunk_id)
        if not candidates:
            return []

        path_raw: list[float] = []
        heading_raw: list[float] = []
        recency_raw: list[float] = []
        for item in candidates:
            source = item.chunk.metadata.source if item.chunk.metadata else ""
            text = item.chunk.text
            path_raw.append(keyword_score(query, source, text))
            heading_raw.append(heading_score(query, text))
            recency_raw.append(recency_raw_score(source, self.knowledge_root))

        max_path = max(path_raw) or 1.0
        max_heading = max(heading_raw) or 1.0
        max_recency = max(recency_raw) or 1.0

        ranked: list[tuple[float, RetrievedChunk]] = []
        weights = self.weights or RetrievalWeights()
        for idx, item in enumerate(candidates):
            source = item.chunk.metadata.source if item.chunk.metadata else ""
            path_norm = path_raw[idx] / max_path
            heading_norm = heading_raw[idx] / max_heading
            recency_norm = recency_raw[idx] / max_recency if max_recency else 0.0
            vector = float(item.score)
            combined = (
                weights.vector * vector
                + weights.path * path_norm
                + weights.heading * heading_norm
                + weights.recency * recency_norm
            )
            breakdown = RetrievalScoreBreakdown(
                vector_score=vector,
                keyword_score=path_norm,
                keyword_raw=path_raw[idx],
                heading_score=heading_norm,
                recency_score=recency_norm,
                combined_score=combined,
            )
            ranked.append((combined, RetrievedChunk(chunk=item.chunk, score=combined, breakdown=breakdown)))

        ranked.sort(key=lambda pair: pair[0], reverse=True)
        return [chunk for _, chunk in ranked[:k]]
