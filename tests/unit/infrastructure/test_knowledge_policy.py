"""Tests for Knowledge embed policy (M5.2.1)."""

from pathlib import Path

import yaml

from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig
from secure_agentic_ai.infrastructure.workspace.knowledge_policy import (
    effective_exclude_globs,
    effective_scan_globs,
    is_path_excluded,
    load_knowledge_policy,
    path_matches_pattern,
)
from secure_agentic_ai.infrastructure.workspace.knowledge_scan import scan_knowledge_files


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
        knowledge_globs=("legacy/**/*.md",),
    )


def _write_policy(root: Path, policy: dict) -> None:
    path = root / ".knowledge-index" / "policy.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(policy, sort_keys=False), encoding="utf-8")


def test_path_matches_pattern_supports_globs() -> None:
    assert path_matches_pattern("01-Base-Point/pro/Backup.md", "01-Base-Point/**/*.md")
    assert not path_matches_pattern("99-Secret/hidden.md", "01-Base-Point/**/*.md")


def test_effective_scan_globs_falls_back_without_policy(tmp_path: Path) -> None:
    config = _config(tmp_path)
    assert effective_scan_globs(config) == ("legacy/**/*.md",)


def test_policy_skips_tier_with_empty_include(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    t1 = root / "01-Base-Point/pro/demo"
    t2 = root / "99-Secret"
    t1.mkdir(parents=True)
    t2.mkdir(parents=True)
    (t1 / "visible.md").write_text("# Visible\n\n" + ("content " * 20), encoding="utf-8")
    (t2 / "secret.md").write_text("# Secret\n\n" + ("hidden " * 20), encoding="utf-8")

    _write_policy(
        root,
        {
            "version": 1,
            "tiers": {
                "T1": {"include": ["01-Base-Point/**/*.md"], "exclude": []},
                "T2": {"include": [], "exclude": []},
            },
        },
    )

    config = _config(root)
    assert effective_scan_globs(config) == ("01-Base-Point/**/*.md",)

    scanned = scan_knowledge_files(config)
    sources = {item.source for item in scanned}
    assert "01-Base-Point/pro/demo/visible.md" in sources
    assert "99-Secret/secret.md" not in sources


def test_policy_exclude_private_files(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    doc_dir = root / "01-Base-Point/pro/demo"
    doc_dir.mkdir(parents=True)
    (doc_dir / "public.md").write_text("# Public\n\n" + ("open " * 20), encoding="utf-8")
    (doc_dir / "notes.private.md").write_text("# Private\n\n" + ("secret " * 20), encoding="utf-8")

    _write_policy(
        root,
        {
            "version": 1,
            "tiers": {
                "T1": {
                    "include": ["01-Base-Point/**/*.md"],
                    "exclude": ["**/*.private.md"],
                },
            },
        },
    )

    config = _config(root)
    assert is_path_excluded("01-Base-Point/pro/demo/notes.private.md", effective_exclude_globs(config))

    scanned = scan_knowledge_files(config)
    sources = {item.source for item in scanned}
    assert "01-Base-Point/pro/demo/public.md" in sources
    assert "01-Base-Point/pro/demo/notes.private.md" not in sources


def test_retrieval_weights_from_policy(tmp_path: Path) -> None:
    from secure_agentic_ai.infrastructure.workspace.knowledge_policy import (
        effective_retrieval_weights,
        retrieval_weights_from_policy,
    )

    root = tmp_path / "knowledge"
    root.mkdir()
    policy_path = root / ".knowledge-index" / "policy.yaml"
    policy_path.parent.mkdir(parents=True)
    policy_path.write_text(
        "version: 1\ntiers:\n  T1:\n    include: ['**/*.md']\n    exclude: []\n"
        "retrieval:\n  weights:\n    vector: 0.5\n    path: 0.3\n    heading: 0.15\n    recency: 0.05\n",
        encoding="utf-8",
    )
    config = _config(root)
    weights = effective_retrieval_weights(config)
    assert weights.vector == 0.5
    assert weights.path == 0.3
    assert weights.heading == 0.15
    assert retrieval_weights_from_policy(load_knowledge_policy(config)).path == 0.3


def test_load_knowledge_policy_parses_retrieval_weights(tmp_path: Path) -> None:
    root = tmp_path / "knowledge"
    _write_policy(
        root,
        {
            "version": 1,
            "tiers": {"T1": {"include": ["**/*.md"], "exclude": []}},
            "retrieval": {"weights": {"vector": 0.6, "path": 0.25}},
        },
    )
    policy = load_knowledge_policy(_config(root))
    assert policy is not None
    assert policy.retrieval_weights == {"vector": 0.6, "path": 0.25}
