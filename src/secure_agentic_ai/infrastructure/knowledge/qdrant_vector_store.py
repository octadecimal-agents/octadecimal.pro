import uuid
from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from secure_agentic_ai.infrastructure.knowledge.fake_embedding_provider import FakeEmbeddingProvider


def _point_id(chunk_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id))


class QdrantVectorStore:
    """Qdrant-backed vector store for Workspace Knowledge chunks (dev/prod)."""

    def __init__(
        self,
        url: str,
        collection: str,
        vector_size: int = FakeEmbeddingProvider.VECTOR_SIZE,
    ) -> None:
        if url == ":memory:":
            self._client = AsyncQdrantClient(location=":memory:", check_compatibility=False)
        else:
            self._client = AsyncQdrantClient(url=url, check_compatibility=False)
        self._collection = collection
        self._vector_size = vector_size

    @property
    def collection(self) -> str:
        return self._collection

    async def ensure_collection(self) -> None:
        names = {item.name for item in (await self._client.get_collections()).collections}
        if self._collection not in names:
            await self._client.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(size=self._vector_size, distance=Distance.COSINE),
            )

    async def count_points(self) -> int:
        info = await self._client.get_collection(self._collection)
        return int(info.points_count or 0)

    async def upsert(self, chunk_id: str, vector: list[float], metadata: dict[str, str]) -> None:
        await self._client.upsert(
            collection_name=self._collection,
            points=[
                PointStruct(
                    id=_point_id(chunk_id),
                    vector=vector,
                    payload={"chunk_id": chunk_id, **metadata},
                )
            ],
        )

    async def similarity_search(
        self, query_vector: list[float], k: int = 5
    ) -> list[tuple[str, float, dict[str, str]]]:
        response = await self._client.query_points(
            collection_name=self._collection,
            query=query_vector,
            limit=k,
            with_payload=True,
        )
        results: list[tuple[str, float, dict[str, str]]] = []
        for hit in response.points:
            payload: dict[str, Any] = hit.payload or {}
            chunk_id = str(payload.get("chunk_id", hit.id))
            metadata = {key: str(value) for key, value in payload.items() if key != "chunk_id"}
            results.append((chunk_id, float(hit.score), metadata))
        return results

    async def close(self) -> None:
        await self._client.close()
