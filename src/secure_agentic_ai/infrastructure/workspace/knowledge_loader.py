from secure_agentic_ai.application.ports import VectorStore
from secure_agentic_ai.application.use_cases import IngestDocumentUseCase
from secure_agentic_ai.infrastructure.knowledge.fake_embedding_provider import FakeEmbeddingProvider
from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig
from secure_agentic_ai.infrastructure.workspace.knowledge_scan import scan_knowledge_files


async def ingest_knowledge_paths(
    config: WorkspaceConfig,
    vector_store: VectorStore,
) -> int:
    embedding = FakeEmbeddingProvider()
    ingest = IngestDocumentUseCase(embedding_provider=embedding, vector_store=vector_store)
    count = 0
    for item in scan_knowledge_files(config):
        await ingest.execute(document_id=item.document_id, text=item.text, source=item.source)
        count += 1
    return count
