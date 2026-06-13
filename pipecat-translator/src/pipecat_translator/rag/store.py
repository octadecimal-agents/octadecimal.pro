from dataclasses import dataclass, field

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from pipecat_translator.rag.embedder import Embedder

COLLECTION_NAME = "pipecat_phrases"


@dataclass
class RAGResult:
    text: str
    pl: str
    en: str
    topic: str
    score: float


class VectorStore:
    def __init__(self, embedder: Embedder):
        self._embedder = embedder
        self._client = QdrantClient(location=":memory:")
        self._dimension = 0
        self._ready = False

    def initialize(self, sample_texts: list[str]) -> None:
        sample_emb = self._embedder.embed(sample_texts[0] if sample_texts else "test")
        self._dimension = len(sample_emb)
        self._client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=self._dimension, distance=Distance.COSINE),
        )
        self._ready = True

    @property
    def ready(self) -> bool:
        return self._ready

    def upsert(self, items: list[dict]) -> None:
        texts = [it["pl"] + " " + it.get("en", "") for it in items]
        embeddings = self._embedder.embed_batch(texts)
        points = [
            PointStruct(id=i, vector=emb, payload=it)
            for i, (emb, it) in enumerate(zip(embeddings, items))
        ]
        self._client.upsert(collection_name=COLLECTION_NAME, points=points)

    def search(self, query: str, top_k: int = 3) -> list[RAGResult]:
        if not self._ready:
            return []
        query_vec = self._embedder.embed(query)
        result = self._client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vec,
            limit=top_k,
        )
        return [
            RAGResult(
                text=h.payload.get("pl", "") + " → " + h.payload.get("en", ""),
                pl=h.payload.get("pl", ""),
                en=h.payload.get("en", ""),
                topic=h.payload.get("topic", ""),
                score=h.score,
            )
            for h in result.points
        ]
