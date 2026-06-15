from pathlib import Path

from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig
from secure_agentic_ai.infrastructure.workspace.knowledge_scan import (
    document_id_for_source,
    scan_knowledge_files,
    sha256_text,
)
from secure_agentic_ai.infrastructure.workspace.knowledge_sync import (
    load_manifest,
    plan_sync,
    save_manifest,
)


def test_document_id_for_source() -> None:
    assert document_id_for_source("01-Base-Point/pro/Backup.md") == "knowledge-01-Base-Point-pro-Backup.md"


def test_plan_sync_detects_added_changed_removed(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    file_a = root / "01-Base-Point/pro/servers/pc-ubuntu/A.md"
    file_b = root / "01-Base-Point/pro/servers/pc-ubuntu/B.md"
    file_a.parent.mkdir(parents=True, exist_ok=True)
    file_a.write_text("# A\n\n" + ("alpha " * 20), encoding="utf-8")
    file_b.write_text("# B\n\n" + ("beta " * 20), encoding="utf-8")

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
        calendar_provider="fixture",
        calendar_fixture_path=tmp_path / "calendar-fixture.json",
        calendar_include=(),
        calendar_exclude=(),
        octa_state_dir=tmp_path / ".octa",
        rag_backend="qdrant",
        qdrant_url="http://127.0.0.1:6335",
        qdrant_collection="knowledge_chunks_dev",
        knowledge_globs=("01-Base-Point/pro/servers/pc-ubuntu/*.md",),
    )

    scanned = scan_knowledge_files(config)
    manifest = {
        "01-Base-Point/pro/servers/pc-ubuntu/A.md": {
            "sha256": "old-hash",
            "document_id": document_id_for_source("01-Base-Point/pro/servers/pc-ubuntu/A.md"),
        },
        "01-Base-Point/pro/servers/pc-ubuntu/Removed.md": {
            "sha256": sha256_text("gone"),
            "document_id": document_id_for_source("01-Base-Point/pro/servers/pc-ubuntu/Removed.md"),
        },
    }

    plan = plan_sync(scanned, manifest)
    assert len(plan.added) == 1
    assert plan.added[0].source.endswith("B.md")
    assert len(plan.changed) == 1
    assert plan.changed[0].source.endswith("A.md")
    assert plan.removed == ("01-Base-Point/pro/servers/pc-ubuntu/Removed.md",)


def test_manifest_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "manifest-dev.json"
    files = {
        "foo.md": {"sha256": "abc", "document_id": "knowledge-foo.md"},
    }
    save_manifest(path, files)
    loaded = load_manifest(path)
    assert loaded["foo.md"]["sha256"] == "abc"
