from pathlib import Path

from secure_agentic_ai.application.ports import VectorStore
from secure_agentic_ai.application.use_cases import IngestDocumentUseCase
from secure_agentic_ai.infrastructure.knowledge.fake_embedding_provider import FakeEmbeddingProvider
from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig
from secure_agentic_ai.infrastructure.workspace.markdown_clean import clean_markdown_for_embed


async def ingest_knowledge_paths(
    config: WorkspaceConfig,
    vector_store: VectorStore,
) -> int:
    embedding = FakeEmbeddingProvider()
    ingest = IngestDocumentUseCase(embedding_provider=embedding, vector_store=vector_store)
    count = 0
    root = config.knowledge_root
    if not root.is_dir():
        return 0

    seen: set[Path] = set()
    for pattern in config.knowledge_globs:
        for path in root.glob(pattern):
            if not path.is_file():
                continue
            canonical = path.resolve()
            if canonical in seen:
                continue
            if path.suffix.lower() != ".md":
                continue
            seen.add(canonical)
            raw = path.read_text(encoding="utf-8", errors="replace")
            cleaned = clean_markdown_for_embed(raw)
            if len(cleaned) < 40:
                continue
            rel = path.relative_to(root).as_posix()
            doc_id = f"knowledge-{rel.replace('/', '-')}"
            await ingest.execute(document_id=doc_id, text=cleaned, source=rel)
            count += 1
    return count
