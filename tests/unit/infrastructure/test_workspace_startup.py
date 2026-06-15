from pathlib import Path

import pytest

from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig
from secure_agentic_ai.infrastructure.workspace.knowledge_sync import manifest_path, sync_knowledge_to_qdrant
from secure_agentic_ai.infrastructure.workspace.state import (
    get_documents_indexed,
    get_workspace_status,
    init_workspace_state,
    reset_for_tests,
)


def _qdrant_config(tmp_path: Path, *, knowledge_root: Path) -> WorkspaceConfig:
    return WorkspaceConfig(
        enabled=True,
        knowledge_root=knowledge_root,
        ledger_path=tmp_path / "ledger.sqlite",
        journal_dir=knowledge_root / "journal",
        llm_provider="dry",
        deepseek_model="deepseek-v4-flash",
        deepseek_base_url="https://api.deepseek.com",
        deepseek_bw_label="",
        minimax_model="MiniMax-M3",
        minimax_base_url="https://api.minimax.io/v1",
        minimax_bw_label="",
        calendar_provider="fixture",
        calendar_fixture_path=tmp_path / "calendar.json",
        calendar_include=(),
        calendar_exclude=(),
        octa_state_dir=tmp_path / ".octa",
        rag_backend="qdrant",
        qdrant_url=":memory:",
        qdrant_collection="knowledge_chunks_startup_test",
        knowledge_globs=("01-Base-Point/pro/servers/pc-ubuntu/*.md",),
    )


def _write_backup_doc(root: Path, *, text: str) -> None:
    doc = root / "01-Base-Point/pro/servers/pc-ubuntu/Backup.md"
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text(text, encoding="utf-8")


@pytest.fixture(autouse=True)
def _clean_state(monkeypatch: pytest.MonkeyPatch) -> None:
    reset_for_tests()
    monkeypatch.delenv("OCTA_REINDEX", raising=False)
    yield
    reset_for_tests()


@pytest.mark.asyncio
async def test_empty_qdrant_bootstraps_on_startup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "knowledge"
    _write_backup_doc(
        root,
        text="# Backup\n\nAutomatyczny backup Qdrant retention na pc-ubuntu.",
    )
    config = _qdrant_config(tmp_path, knowledge_root=root)
    monkeypatch.setenv("WORKSPACE_ENABLED", "1")
    monkeypatch.setenv("RAG_BACKEND", "qdrant")
    monkeypatch.setenv("QDRANT_URL", ":memory:")
    monkeypatch.setenv("QDRANT_COLLECTION", config.qdrant_collection)
    monkeypatch.setenv("KNOWLEDGE_ROOT", str(root))
    monkeypatch.setenv("OCTA_LEDGER", str(config.ledger_path))
    monkeypatch.setenv("OCTA_REINDEX", "0")

    indexed = await init_workspace_state()

    assert indexed >= 1
    assert get_documents_indexed() >= 1
    assert manifest_path(config).is_file()
    status, issues = get_workspace_status()
    assert status == "ok"
    assert issues == []


@pytest.mark.asyncio
async def test_startup_runs_incremental_sync_when_file_changed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "knowledge"
    _write_backup_doc(
        root,
        text="# Backup\n\nOriginal backup procedure for Qdrant.",
    )
    config = _qdrant_config(tmp_path, knowledge_root=root)
    monkeypatch.setenv("WORKSPACE_ENABLED", "1")
    monkeypatch.setenv("RAG_BACKEND", "qdrant")
    monkeypatch.setenv("QDRANT_URL", ":memory:")
    monkeypatch.setenv("QDRANT_COLLECTION", config.qdrant_collection)
    monkeypatch.setenv("KNOWLEDGE_ROOT", str(root))
    monkeypatch.setenv("OCTA_LEDGER", str(config.ledger_path))

    await init_workspace_state()
    first_count = get_documents_indexed()

    _write_backup_doc(
        root,
        text="# Backup\n\nUpdated backup procedure for Qdrant snapshots.",
    )

    await init_workspace_state()

    assert get_documents_indexed() >= first_count
    assert manifest_path(config).is_file()


@pytest.mark.asyncio
async def test_missing_knowledge_root_sets_degraded_status(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    missing = tmp_path / "missing-knowledge"
    monkeypatch.setenv("WORKSPACE_ENABLED", "1")
    monkeypatch.setenv("RAG_BACKEND", "memory")
    monkeypatch.setenv("KNOWLEDGE_ROOT", str(missing))
    monkeypatch.setenv("OCTA_LEDGER", str(tmp_path / "ledger.sqlite"))

    indexed = await init_workspace_state()

    assert indexed == 0
    status, issues = get_workspace_status()
    assert status == "degraded"
    assert any("KNOWLEDGE_ROOT not found" in issue for issue in issues)


@pytest.mark.asyncio
async def test_qdrant_unreachable_fails_loud(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "knowledge"
    root.mkdir()
    monkeypatch.setenv("WORKSPACE_ENABLED", "1")
    monkeypatch.setenv("RAG_BACKEND", "qdrant")
    monkeypatch.setenv("QDRANT_URL", "http://127.0.0.1:1")
    monkeypatch.setenv("QDRANT_COLLECTION", "knowledge_chunks_dev")
    monkeypatch.setenv("KNOWLEDGE_ROOT", str(root))
    monkeypatch.setenv("OCTA_LEDGER", str(tmp_path / "ledger.sqlite"))

    with pytest.raises(RuntimeError, match="Qdrant is unreachable"):
        await init_workspace_state()


@pytest.mark.asyncio
async def test_sync_reuses_existing_store_without_closing(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    _write_backup_doc(
        root,
        text="# Backup\n\nAutomatyczny backup stacku HYDRA Qdrant retention na pc-ubuntu dev.",
    )
    config = _qdrant_config(tmp_path, knowledge_root=root)

    from secure_agentic_ai.infrastructure.knowledge.qdrant_vector_store import QdrantVectorStore

    store = QdrantVectorStore(url=":memory:", collection=config.qdrant_collection)
    await sync_knowledge_to_qdrant(config, store=store)
    count_after_first = await store.count_points()
    await sync_knowledge_to_qdrant(config, store=store)
    count_after_second = await store.count_points()
    await store.close()

    assert count_after_first >= 1
    assert count_after_second == count_after_first
