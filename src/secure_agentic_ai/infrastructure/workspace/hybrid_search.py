import re

from secure_agentic_ai.application.use_cases import RetrieveContextUseCase
from secure_agentic_ai.domain.knowledge import RetrievedChunk, RetrievalScoreBreakdown

_TOKEN = re.compile(r"[a-z0-9\u0105-\u017c]{3,}", re.IGNORECASE)


def _query_tokens(query: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(query)]


def keyword_score(query: str, source: str, text: str) -> float:
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
    # Prefer canonical runbooks over nested agent stubs when keywords tie.
    if "/.claude/" in source or ("/agents/" in source and "agent" in filename):
        score *= 0.85
    return score / len(tokens)


class HybridKnowledgeSearch:
    """Vector search with keyword re-ranking for path identifiers (MVP hybrid RRF-lite)."""

    def __init__(self, retrieve: RetrieveContextUseCase, vector_weight: float = 0.25) -> None:
        self._retrieve = retrieve
        self._vector_weight = vector_weight

    async def search(self, query: str, k: int = 5) -> list[RetrievedChunk]:
        # MVP corpus is small (~250 docs); wider pool helps filename-heavy runbooks surface.
        candidates = await self._retrieve.execute(query, k=max(k * 8, 100))
        tokens = _query_tokens(query)
        if tokens:
            title_hint = " ".join(token.capitalize() for token in tokens[:2])
            extra = await self._retrieve.execute(f"{title_hint} {query}", k=20)
            seen = {c.chunk.chunk_id for c in candidates}
            for item in extra:
                if item.chunk.chunk_id not in seen:
                    candidates.append(item)
                    seen.add(item.chunk.chunk_id)
        if not candidates:
            return []

        max_kw = max(
            keyword_score(
                query,
                c.chunk.metadata.source if c.chunk.metadata else "",
                c.chunk.text,
            )
            for c in candidates
        )
        max_kw = max_kw or 1.0

        ranked: list[tuple[float, RetrievedChunk]] = []
        for item in candidates:
            source = item.chunk.metadata.source if item.chunk.metadata else ""
            kw_raw = keyword_score(query, source, item.chunk.text)
            kw = kw_raw / max_kw
            combined = self._vector_weight * item.score + (1.0 - self._vector_weight) * kw
            breakdown = RetrievalScoreBreakdown(
                vector_score=float(item.score),
                keyword_score=kw,
                keyword_raw=kw_raw,
                combined_score=combined,
            )
            ranked.append(
                (
                    combined,
                    RetrievedChunk(chunk=item.chunk, score=combined, breakdown=breakdown),
                )
            )

        ranked.sort(key=lambda pair: pair[0], reverse=True)
        return [chunk for _, chunk in ranked[:k]]
