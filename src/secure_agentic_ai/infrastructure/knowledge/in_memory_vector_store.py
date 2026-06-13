import math


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if not norm_a or not norm_b:
        return 0.0
    return dot / (norm_a * norm_b)


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._vectors: dict[str, list[float]] = {}
        self._metadata: dict[str, dict[str, str]] = {}

    async def upsert(self, chunk_id: str, vector: list[float], metadata: dict[str, str]) -> None:
        self._vectors[chunk_id] = vector
        self._metadata[chunk_id] = metadata

    async def similarity_search(self, query_vector: list[float], k: int = 5) -> list[tuple[str, float, dict[str, str]]]:
        scored = []
        for chunk_id, vector in self._vectors.items():
            score = _cosine_similarity(query_vector, vector)
            scored.append((chunk_id, score, self._metadata.get(chunk_id, {})))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]
