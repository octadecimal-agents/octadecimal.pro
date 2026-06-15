import json
import logging
import os

from secure_agentic_ai.domain.knowledge import RetrievedChunk

logger = logging.getLogger("secure_agentic_ai.retrieval")


def debug_retrieval_enabled() -> bool:
    return os.environ.get("WORKSPACE_DEBUG", "").lower() in {"1", "true", "yes"}


def log_retrieval_query(query: str, hits: list[RetrievedChunk]) -> None:
    payload = {
        "event": "retrieval",
        "query": query,
        "top_sources": [
            hit.chunk.metadata.source if hit.chunk.metadata else ""
            for hit in hits
        ],
        "scores": [
            {
                "source": hit.chunk.metadata.source if hit.chunk.metadata else "",
                "combined": round(float(hit.score), 4),
                "vector": round(hit.breakdown.vector_score, 4) if hit.breakdown else None,
                "keyword": round(hit.breakdown.keyword_score, 4) if hit.breakdown else None,
                "keyword_raw": round(hit.breakdown.keyword_raw, 4) if hit.breakdown else None,
            }
            for hit in hits
        ],
    }
    logger.info(json.dumps(payload, ensure_ascii=False))
