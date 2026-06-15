"""Tests for octa-knowledge-sync-m1.sh."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "octa-knowledge-sync-m1.sh"


def test_octa_knowledge_sync_m1_script_has_valid_bash_syntax() -> None:
    import subprocess

    subprocess.run(["bash", "-n", str(SCRIPT)], check=True)


def test_octa_knowledge_sync_m1_excludes_secrets() -> None:
    text = SCRIPT.read_text()
    assert ".secrets/" in text
    assert ".knowledge-index/" in text
