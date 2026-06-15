import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "octa-knowledge-sync-dev.sh"


def test_octa_knowledge_sync_dev_script_has_valid_bash_syntax() -> None:
    result = subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


def test_octa_knowledge_sync_dev_refuses_non_dev_collection() -> None:
    env = os.environ.copy()
    env.update(
        {
            "QDRANT_COLLECTION": "knowledge_chunks_prod",
            "QDRANT_URL": "http://127.0.0.1:6335",
            "OCTA_SYNC_SKIP_QDRANT": "1",
            "OCTA_SYNC_LOG": str(ROOT / "data" / "test-embed-sync-refuse.log"),
        }
    )
    log_path = Path(env["OCTA_SYNC_LOG"])
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.unlink(missing_ok=True)

    result = subprocess.run(["bash", str(SCRIPT)], cwd=ROOT, env=env, capture_output=True, text=True, check=False)
    assert result.returncode == 1
    assert log_path.is_file()
    log_text = log_path.read_text(encoding="utf-8")
    assert "knowledge_chunks_dev" in log_text


def test_octa_knowledge_sync_dev_refuses_remote_qdrant_url() -> None:
    env = os.environ.copy()
    env.update(
        {
            "QDRANT_COLLECTION": "knowledge_chunks_dev",
            "QDRANT_URL": "https://qdrant.example.com:6333",
            "OCTA_SYNC_SKIP_QDRANT": "1",
            "OCTA_SYNC_LOG": str(ROOT / "data" / "test-embed-sync-remote.log"),
        }
    )
    log_path = Path(env["OCTA_SYNC_LOG"])
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.unlink(missing_ok=True)

    result = subprocess.run(["bash", str(SCRIPT)], cwd=ROOT, env=env, capture_output=True, text=True, check=False)
    assert result.returncode == 1
    assert "6335" in log_path.read_text(encoding="utf-8")
