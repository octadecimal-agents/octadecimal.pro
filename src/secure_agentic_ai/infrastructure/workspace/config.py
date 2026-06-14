import os
from dataclasses import dataclass
from pathlib import Path


def _expand(path: str) -> Path:
    return Path(path).expanduser().resolve()


@dataclass(frozen=True)
class WorkspaceConfig:
    enabled: bool
    knowledge_root: Path
    ledger_path: Path
    journal_dir: Path
    llm_provider: str
    knowledge_globs: tuple[str, ...]

    @classmethod
    def from_env(cls) -> "WorkspaceConfig":
        knowledge_root = _expand(os.environ.get("KNOWLEDGE_ROOT", "~/Developer/Knowledge"))
        return cls(
            enabled=os.environ.get("WORKSPACE_ENABLED", "").lower() in {"1", "true", "yes"},
            knowledge_root=knowledge_root,
            ledger_path=_expand(os.environ.get("OCTA_LEDGER", "~/.octa/ledger.sqlite")),
            journal_dir=knowledge_root / "02-6-Rooms-Model" / "_system" / "journal",
            llm_provider=os.environ.get("LLM_PROVIDER", "dry").lower(),
            knowledge_globs=(
                "01-Base-Point/pro/servers/pc-ubuntu/**/*.md",
                "01-Base-Point/pro/projects/octa-os/**/*.md",
                "01-Base-Point/pro/knowledge-embeddings.md",
                "02-6-Rooms-Model/Operacje/serwer/**/*.md",
            ),
        )
