"""Integration tests for full T1 Knowledge scan (M5.2.2)."""

from pathlib import Path

import pytest
import yaml

from secure_agentic_ai.application.use_cases import RetrieveContextUseCase
from secure_agentic_ai.infrastructure.knowledge.fake_embedding_provider import FakeEmbeddingProvider
from secure_agentic_ai.infrastructure.knowledge.in_memory_vector_store import InMemoryVectorStore
from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig
from secure_agentic_ai.infrastructure.workspace.hybrid_search import HybridKnowledgeSearch
from secure_agentic_ai.infrastructure.workspace.knowledge_loader import ingest_knowledge_paths
from secure_agentic_ai.infrastructure.workspace.knowledge_scan import scan_knowledge_files


def _write_policy(root: Path) -> None:
    policy = {
        "version": 1,
        "tiers": {
            "T1": {
                "include": [
                    "01-Base-Point/pro/servers/pc-ubuntu/**/*.md",
                    "01-Base-Point/pro/projects/octa-os/**/*.md",
                ],
                "exclude": ["**/*.private.md"],
            },
            "T2": {"include": [], "exclude": []},
        },
    }
    path = root / ".knowledge-index" / "policy.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(policy), encoding="utf-8")


def _config(root: Path) -> WorkspaceConfig:
    return WorkspaceConfig(
        enabled=True,
        knowledge_root=root,
        ledger_path=root / "ledger.sqlite",
        journal_dir=root / "journal",
        llm_provider="dry",
        deepseek_model="deepseek-v4-flash",
        deepseek_base_url="https://api.deepseek.com",
        deepseek_bw_label="",
        minimax_model="MiniMax-M3",
        minimax_base_url="https://api.minimax.io/v1",
        minimax_bw_label="",
        calendar_provider="fixture",
        calendar_fixture_path=root / "calendar.json",
        calendar_include=(),
        calendar_exclude=(),
        octa_state_dir=root / ".octa",
        rag_backend="memory",
        qdrant_url="http://127.0.0.1:6335",
        qdrant_collection="knowledge_chunks_dev",
        knowledge_globs=("01-Base-Point/pro/servers/pc-ubuntu/**/*.md",),
    )


def test_t1_policy_scan_exceeds_mvp_demo_threshold(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    _write_policy(root)

    for idx in range(80):
        path = root / f"01-Base-Point/pro/projects/octa-os/docs/doc-{idx:03d}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# Doc {idx}\n\n" + ("paragraph " * 15), encoding="utf-8")

    backup = root / "01-Base-Point/pro/servers/pc-ubuntu/Backup.md"
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text(
        "# Backup\n\nAutomatyczny backup stacku HYDRA Qdrant retention na pc-ubuntu.",
        encoding="utf-8",
    )

    private = root / "01-Base-Point/pro/projects/octa-os/secret.private.md"
    private.write_text("# Secret\n\n" + ("hidden " * 20), encoding="utf-8")

    config = _config(root)
    scanned = scan_knowledge_files(config)

    assert len(scanned) >= 81
    sources = {item.source for item in scanned}
    assert "01-Base-Point/pro/servers/pc-ubuntu/Backup.md" in sources
    assert "01-Base-Point/pro/projects/octa-os/secret.private.md" not in sources


@pytest.mark.asyncio
async def test_full_t1_ingest_backup_query_still_hits_runbook(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    _write_policy(root)

    for idx in range(20):
        path = root / f"01-Base-Point/pro/projects/octa-os/noise-{idx}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"# Noise {idx}\n\nbash tutorial elearning exercises unrelated content.",
            encoding="utf-8",
        )

    backup = root / "01-Base-Point/pro/servers/pc-ubuntu/Backup.md"
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text(
        "# Backup\n\nAutomatyczny backup Qdrant na pc-ubuntu retention 30 dni.",
        encoding="utf-8",
    )

    config = _config(root)
    store = InMemoryVectorStore()
    indexed = await ingest_knowledge_paths(config, store)
    assert indexed >= 21

    hybrid = HybridKnowledgeSearch(
        retrieve=RetrieveContextUseCase(FakeEmbeddingProvider(), store),
    )
    results = await hybrid.search("jak backup Qdrant?", k=3)
    sources = [r.chunk.metadata.source if r.chunk.metadata else "" for r in results]
    assert any("Backup.md" in source for source in sources)
