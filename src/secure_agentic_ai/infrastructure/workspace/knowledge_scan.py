import hashlib
from dataclasses import dataclass
from pathlib import Path

from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig
from secure_agentic_ai.infrastructure.workspace.knowledge_policy import (
    effective_exclude_globs,
    effective_scan_globs,
    is_path_excluded,
)
from secure_agentic_ai.infrastructure.workspace.markdown_clean import clean_markdown_for_embed


@dataclass(frozen=True)
class KnowledgeFile:
    path: Path
    source: str
    document_id: str
    sha256: str
    text: str


def document_id_for_source(source: str) -> str:
    return f"knowledge-{source.replace('/', '-')}"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def scan_knowledge_files(config: WorkspaceConfig) -> list[KnowledgeFile]:
    root = config.knowledge_root
    if not root.is_dir():
        return []

    seen: set[Path] = set()
    files: list[KnowledgeFile] = []
    exclude_patterns = effective_exclude_globs(config)

    for pattern in effective_scan_globs(config):
        for path in root.glob(pattern):
            if not path.is_file() or path.suffix.lower() != ".md":
                continue
            canonical = path.resolve()
            if canonical in seen:
                continue
            seen.add(canonical)

            rel = path.relative_to(root).as_posix()
            if is_path_excluded(rel, exclude_patterns):
                continue

            raw = path.read_text(encoding="utf-8", errors="replace")
            cleaned = clean_markdown_for_embed(raw)
            if len(cleaned) < 40:
                continue

            files.append(
                KnowledgeFile(
                    path=path,
                    source=rel,
                    document_id=document_id_for_source(rel),
                    sha256=sha256_text(cleaned),
                    text=cleaned,
                )
            )

    return sorted(files, key=lambda item: item.source)
