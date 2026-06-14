from secure_agentic_ai.application.use_cases import RetrieveContextUseCase
from secure_agentic_ai.infrastructure.knowledge.fake_embedding_provider import FakeEmbeddingProvider
from secure_agentic_ai.infrastructure.knowledge.in_memory_vector_store import InMemoryVectorStore
from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig
from secure_agentic_ai.infrastructure.workspace.knowledge_loader import ingest_knowledge_paths
from secure_agentic_ai.infrastructure.workspace.ledger import WorkspaceLedger

_ledger: WorkspaceLedger | None = None
_vector_store: InMemoryVectorStore | None = None
_config: WorkspaceConfig | None = None
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


def get_vector_store() -> InMemoryVectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = InMemoryVectorStore()
    return _vector_store


async def init_workspace_state() -> int:
    global _initialized, _documents_indexed
    config = get_config()
    store = get_vector_store()
    get_ledger().seed_demo_tasks()
    if not _initialized:
        _documents_indexed = await ingest_knowledge_paths(config, store)
        _initialized = True
    return _documents_indexed


def get_documents_indexed() -> int:
    return _documents_indexed


def get_retrieve_use_case() -> RetrieveContextUseCase:
    return RetrieveContextUseCase(
        embedding_provider=FakeEmbeddingProvider(),
        vector_store=get_vector_store(),
    )


def reset_for_tests() -> None:
    global _ledger, _vector_store, _config, _initialized, _documents_indexed
    _ledger = None
    _vector_store = None
    _config = None
    _initialized = False
    _documents_indexed = 0
