import os
from dataclasses import dataclass
from pathlib import Path


def _expand(path: str) -> Path:
    return Path(path).expanduser().resolve()


def _csv_tuple(raw: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in raw.split(",") if part.strip())


@dataclass(frozen=True)
class WorkspaceConfig:
    enabled: bool
    knowledge_root: Path
    ledger_path: Path
    journal_dir: Path
    llm_provider: str
    deepseek_model: str
    deepseek_base_url: str
    deepseek_bw_label: str
    minimax_model: str
    minimax_base_url: str
    minimax_bw_label: str
    calendar_provider: str
    calendar_fixture_path: Path
    calendar_include: tuple[str, ...]
    calendar_exclude: tuple[str, ...]
    octa_state_dir: Path
    rag_backend: str
    qdrant_url: str
    qdrant_collection: str
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
            deepseek_model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash"),
            deepseek_base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            deepseek_bw_label=os.environ.get("DEEPSEEK_BW_LABEL", ""),
            minimax_model=os.environ.get("MINIMAX_MODEL", "MiniMax-M3"),
            minimax_base_url=os.environ.get("MINIMAX_BASE_URL", "https://api.minimax.io/v1"),
            minimax_bw_label=os.environ.get("MINIMAX_BW_LABEL", ""),
            calendar_provider=os.environ.get("CALENDAR_PROVIDER", "auto").lower(),
            calendar_fixture_path=_expand(os.environ.get("OCTA_CALENDAR_FIXTURE", "~/.octa/calendar-fixture.json")),
            calendar_include=_csv_tuple(os.environ.get("CALENDAR_INCLUDE", "")),
            calendar_exclude=_csv_tuple(os.environ.get("CALENDAR_EXCLUDE", "")),
            octa_state_dir=_expand(os.environ.get("OCTA_STATE_DIR", "~/.octa")),
            rag_backend=os.environ.get("RAG_BACKEND", "memory").lower(),
            qdrant_url=os.environ.get("QDRANT_URL", "http://127.0.0.1:6335"),
            qdrant_collection=os.environ.get("QDRANT_COLLECTION", "knowledge_chunks_dev"),
            knowledge_globs=(
                "01-Base-Point/pro/servers/pc-ubuntu/**/*.md",
                "01-Base-Point/pro/projects/octa-os/**/*.md",
                "01-Base-Point/pro/knowledge-embeddings.md",
                "02-6-Rooms-Model/Operacje/serwer/**/*.md",
                "02-6-Rooms-Model/_system/**/*.md",
            ),
        )
