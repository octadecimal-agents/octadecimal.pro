import os

from secure_agentic_ai.application.ports import ChatCompletionProvider
from secure_agentic_ai.application.use_cases import RetrieveContextUseCase
from secure_agentic_ai.infrastructure.knowledge.fake_embedding_provider import FakeEmbeddingProvider
from secure_agentic_ai.infrastructure.knowledge.in_memory_vector_store import InMemoryVectorStore
from secure_agentic_ai.infrastructure.knowledge.qdrant_vector_store import QdrantVectorStore
from secure_agentic_ai.infrastructure.llm.factory import build_chat_provider
from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig
from secure_agentic_ai.infrastructure.workspace.hybrid_search import HybridKnowledgeSearch
from secure_agentic_ai.infrastructure.workspace.knowledge_loader import ingest_knowledge_paths
from secure_agentic_ai.infrastructure.workspace.knowledge_policy import effective_retrieval_weights
from secure_agentic_ai.infrastructure.workspace.ledger import WorkspaceLedger

VectorStoreBackend = InMemoryVectorStore | QdrantVectorStore

_ledger: WorkspaceLedger | None = None
_vector_store: VectorStoreBackend | None = None
_config: WorkspaceConfig | None = None
_chat_provider: ChatCompletionProvider | None = None
_initialized = False
_documents_indexed = 0


def get_config() -> WorkspaceConfig:
    global _config
    if _config is None:
        _config = WorkspaceConfig.from_env()
    return _config


def get_ledger() -> WorkspaceLedger:
    global _ledger
    if _ledger is None:
        _ledger = WorkspaceLedger(get_config().ledger_path)
    return _ledger


def _should_reindex() -> bool:
    return os.environ.get("OCTA_REINDEX", "").lower() in {"1", "true", "yes"}


def get_vector_store() -> VectorStoreBackend:
    global _vector_store
    if _vector_store is None:
        config = get_config()
        if config.rag_backend == "qdrant":
            _vector_store = QdrantVectorStore(
                url=config.qdrant_url,
                collection=config.qdrant_collection,
            )
        else:
            _vector_store = InMemoryVectorStore()
    return _vector_store


async def init_workspace_state() -> int:
    global _initialized, _documents_indexed
    config = get_config()
    store = get_vector_store()
    get_ledger().seed_demo_tasks()

    reindex = _should_reindex()
    if isinstance(store, QdrantVectorStore):
        await store.ensure_collection()
        existing = await store.count_points()
        if existing == 0 or reindex:
            _documents_indexed = await ingest_knowledge_paths(config, store)
        else:
            _documents_indexed = existing
        _initialized = True
        return _documents_indexed

    if not _initialized or reindex:
        _documents_indexed = await ingest_knowledge_paths(config, store)
        _initialized = True
    return _documents_indexed


def get_documents_indexed() -> int:
    return _documents_indexed


def get_rag_backend_label() -> str:
    config = get_config()
    if config.rag_backend == "qdrant":
        return f"qdrant:{config.qdrant_collection}@{config.qdrant_url}"
    return "memory"


async def get_chat_provider() -> ChatCompletionProvider:
    global _chat_provider
    if _chat_provider is None:
        _chat_provider = await build_chat_provider(get_config())
    return _chat_provider


def get_llm_label() -> str:
    if _chat_provider is not None:
        return _chat_provider.label
    config = get_config()
    if config.llm_provider == "minimax":
        return f"minimax:{config.minimax_model}"
    if config.llm_provider == "deepseek":
        return f"deepseek:{config.deepseek_model}"
    return config.llm_provider


def get_hybrid_search() -> HybridKnowledgeSearch:
    config = get_config()
    return HybridKnowledgeSearch(
        retrieve=get_retrieve_use_case(),
        weights=effective_retrieval_weights(config),
        knowledge_root=config.knowledge_root,
    )


def get_retrieve_use_case() -> RetrieveContextUseCase:
    return RetrieveContextUseCase(
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=get_vector_store(),
    )


async def shutdown_workspace_state() -> None:
    global _vector_store
    if isinstance(_vector_store, QdrantVectorStore):
        await _vector_store.close()
        _vector_store = None


def reset_for_tests() -> None:
    global _ledger, _vector_store, _config, _chat_provider, _initialized, _documents_indexed
    _ledger = None
    _vector_store = None
    _config = None
    _chat_provider = None
    _initialized = False
    _documents_indexed = 0
