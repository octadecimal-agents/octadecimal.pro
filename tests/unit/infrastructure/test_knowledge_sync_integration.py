import pytest

from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig
from secure_agentic_ai.infrastructure.workspace.knowledge_sync import manifest_path, sync_knowledge_to_qdrant


@pytest.mark.asyncio
async def test_sync_knowledge_to_qdrant_memory(tmp_path) -> None:
    root = tmp_path / "knowledge"
    doc = root / "01-Base-Point/pro/servers/pc-ubuntu/Backup.md"
    doc.parent.mkdir(parents=True)
    doc.write_text(
        "# Backup\n\nAutomatyczny backup stacku HYDRA na pc-ubuntu Qdrant retention 30 days.",
        encoding="utf-8",
    )

    config = WorkspaceConfig(
        enabled=True,
        knowledge_root=root,
        ledger_path=tmp_path / "ledger.sqlite",
        journal_dir=root / "journal",
        llm_provider="dry",
        deepseek_model="deepseek-v4-flash",
        deepseek_base_url="https://api.deepseek.com",
        deepseek_bw_label="",
        minimax_model="MiniMax-M3",
        minimax_base_url="https://api.minimax.io/v1",
        minimax_bw_label="",
        rag_backend="qdrant",
        qdrant_url=":memory:",
        qdrant_collection="knowledge_chunks_test",
        knowledge_globs=("01-Base-Point/pro/servers/pc-ubuntu/*.md",),
    )

    first = await sync_knowledge_to_qdrant(config)
    assert first.added == 1
    assert first.changed == 0

    second = await sync_knowledge_to_qdrant(config)
    assert second.added == 0
    assert second.changed == 0
    assert second.unchanged == 1

    doc.write_text(
        "# Backup\n\nUpdated backup procedure for Qdrant snapshots on pc-ubuntu.",
        encoding="utf-8",
    )
    third = await sync_knowledge_to_qdrant(config)
    assert third.changed == 1

    manifest = manifest_path(config).read_text(encoding="utf-8")
    assert "Updated backup procedure" not in manifest
    assert "Backup.md" in manifest
