import hashlib


class FakeEmbeddingProvider:
    VECTOR_SIZE = 64

    async def embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode()).digest()
        # SHA-256 is 32 bytes; extend deterministically to VECTOR_SIZE for Qdrant collections.
        extended = digest + hashlib.sha256(b"pad:" + digest).digest()
        return [byte / 255.0 for byte in extended[: self.VECTOR_SIZE]]
