#!/usr/bin/env python3
"""Incremental Knowledge embed sync for Octa Workspace dev Qdrant."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys


def _apply_dev_defaults() -> None:
    os.environ.setdefault("KNOWLEDGE_ROOT", os.path.expanduser("~/Developer/Knowledge"))
    os.environ.setdefault("QDRANT_URL", "http://127.0.0.1:6335")
    os.environ.setdefault("QDRANT_COLLECTION", "knowledge_chunks_dev")


async def _run_sync(*, dry_run: bool) -> int:
    from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig
    from secure_agentic_ai.infrastructure.workspace.knowledge_sync import sync_knowledge_to_qdrant

    config = WorkspaceConfig.from_env()
    result = await sync_knowledge_to_qdrant(config, dry_run=dry_run)
    mode = "dry-run" if result.dry_run else "sync"
    print(
        f"{mode}: scanned={result.scanned} added={result.added} "
        f"changed={result.changed} removed={result.removed} unchanged={result.unchanged}"
    )
    return 0


def _run_scan() -> int:
    from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig
    from secure_agentic_ai.infrastructure.workspace.knowledge_policy import (
        effective_scan_globs,
        policy_path,
    )
    from secure_agentic_ai.infrastructure.workspace.knowledge_scan import scan_knowledge_files

    config = WorkspaceConfig.from_env()
    files = scan_knowledge_files(config)
    policy = policy_path(config)
    print(f"knowledge_root={config.knowledge_root}")
    print(f"policy={'found' if policy.is_file() else 'missing (using config globs)'}")
    print(f"globs={effective_scan_globs(config)}")
    print(f"files={len(files)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Embed Knowledge Markdown into Qdrant.")
    sub = parser.add_subparsers(dest="command", required=True)

    sync_parser = sub.add_parser("sync", help="Incremental sync changed files to Qdrant")
    sync_parser.add_argument(
        "--dev",
        action="store_true",
        help="Use dev defaults (Qdrant :6335, collection knowledge_chunks_dev)",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show diff without writing to Qdrant or manifest",
    )

    scan_parser = sub.add_parser("scan", help="List T1 files matched by embed policy (no Qdrant write)")
    scan_parser.add_argument(
        "--dev",
        action="store_true",
        help="Use dev KNOWLEDGE_ROOT default",
    )

    args = parser.parse_args(argv)
    if args.command == "sync":
        if args.dev:
            _apply_dev_defaults()
        return asyncio.run(_run_sync(dry_run=args.dry_run))

    if args.command == "scan":
        if args.dev:
            _apply_dev_defaults()
        return _run_scan()

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
