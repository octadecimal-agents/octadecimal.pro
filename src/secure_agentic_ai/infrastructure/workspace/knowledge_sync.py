import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from secure_agentic_ai.application.use_cases import IngestDocumentUseCase
from secure_agentic_ai.infrastructure.knowledge.fake_embedding_provider import FakeEmbeddingProvider
from secure_agentic_ai.infrastructure.knowledge.qdrant_vector_store import QdrantVectorStore
from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig
from secure_agentic_ai.infrastructure.workspace.knowledge_scan import KnowledgeFile, scan_knowledge_files


@dataclass(frozen=True)
class SyncPlan:
    added: tuple[KnowledgeFile, ...]
    changed: tuple[KnowledgeFile, ...]
    removed: tuple[str, ...]


@dataclass(frozen=True)
class SyncResult:
    scanned: int
    added: int
    changed: int
    removed: int
    unchanged: int
    dry_run: bool


def manifest_path(config: WorkspaceConfig) -> Path:
    return config.knowledge_root / ".knowledge-index" / "manifest-dev.json"


def load_manifest(path: Path) -> dict[str, dict[str, str]]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    files = data.get("files")
    if not isinstance(files, dict):
        return {}
    return {str(key): value for key, value in files.items() if isinstance(value, dict)}


def save_manifest(path: Path, files: dict[str, dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "updated_at": datetime.now(UTC).isoformat(),
        "files": files,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def manifest_sync_status(config: WorkspaceConfig) -> tuple[int | None, str | None]:
    """Return manifest age in seconds and optional updated_at ISO timestamp."""
    path = manifest_path(config)
    if not path.is_file():
        return None, None
    age_seconds = int(datetime.now(UTC).timestamp() - path.stat().st_mtime)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return age_seconds, None
    updated_at = data.get("updated_at")
    if isinstance(updated_at, str):
        return age_seconds, updated_at
    return age_seconds, None


def plan_sync(
    scanned: list[KnowledgeFile],
    manifest: dict[str, dict[str, str]],
) -> SyncPlan:
    scanned_by_source = {item.source: item for item in scanned}
    manifest_sources = set(manifest)

    added: list[KnowledgeFile] = []
    changed: list[KnowledgeFile] = []
    for source, item in scanned_by_source.items():
        previous = manifest.get(source)
        if previous is None:
            added.append(item)
            continue
        if previous.get("sha256") != item.sha256:
            changed.append(item)

    removed = sorted(source for source in manifest_sources if source not in scanned_by_source)
    return SyncPlan(
        added=tuple(added),
        changed=tuple(changed),
        removed=tuple(removed),
    )


async def sync_knowledge_to_qdrant(
    config: WorkspaceConfig,
    *,
    dry_run: bool = False,
) -> SyncResult:
    scanned = scan_knowledge_files(config)
    path = manifest_path(config)
    manifest = load_manifest(path)
    plan = plan_sync(scanned, manifest)

    unchanged = len(scanned) - len(plan.added) - len(plan.changed)

    if dry_run:
        return SyncResult(
            scanned=len(scanned),
            added=len(plan.added),
            changed=len(plan.changed),
            removed=len(plan.removed),
            unchanged=unchanged,
            dry_run=True,
        )

    store = QdrantVectorStore(url=config.qdrant_url, collection=config.qdrant_collection)
    await store.ensure_collection()
    ingest = IngestDocumentUseCase(embedding_provider=FakeEmbeddingProvider(), vector_store=store)

    try:
        for source in plan.removed:
            document_id = manifest[source].get("document_id") or f"knowledge-{source.replace('/', '-')}"
            await store.delete_by_document_id(document_id)

        for item in (*plan.added, *plan.changed):
            await store.delete_by_document_id(item.document_id)
            await ingest.execute(document_id=item.document_id, text=item.text, source=item.source)

        next_manifest = {
            item.source: {
                "sha256": item.sha256,
                "document_id": item.document_id,
            }
            for item in scanned
        }
        save_manifest(path, next_manifest)
    finally:
        await store.close()

    return SyncResult(
        scanned=len(scanned),
        added=len(plan.added),
        changed=len(plan.changed),
        removed=len(plan.removed),
        unchanged=unchanged,
        dry_run=False,
    )
