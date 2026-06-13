import hashlib


class FakeEmbeddingProvider:
    VECTOR_SIZE = 64

    async def embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode()).digest()
        return [b / 255.0 for b in digest[: self.VECTOR_SIZE]]
