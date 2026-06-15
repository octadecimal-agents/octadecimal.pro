import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "octa-workspace-api-dev.sh"
ENV_SCRIPT = ROOT / "scripts" / "octa-workspace-env.sh"
INSTALL_SCRIPT = ROOT / "scripts" / "install-workspace-api-launchd.sh"
PLIST_TEMPLATE = ROOT / "scripts" / "launchd" / "pl.octadecimal.workspace-api-dev.plist.template"


def test_octa_workspace_api_dev_script_has_valid_bash_syntax() -> None:
    for path in (SCRIPT, ENV_SCRIPT, INSTALL_SCRIPT):
        result = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True, check=False)
        assert result.returncode == 0, f"{path.name}: {result.stderr}"


def test_workspace_api_plist_template_exists() -> None:
    assert PLIST_TEMPLATE.is_file()
    text = PLIST_TEMPLATE.read_text(encoding="utf-8")
    assert "pl.octadecimal.workspace-api-dev" in text
    assert "@REPO_ROOT@" in text


def test_octa_workspace_api_dev_refuses_non_localhost_host() -> None:
    env = os.environ.copy()
    env.update(
        {
            "WORKSPACE_HOST": "0.0.0.0",
            "WORKSPACE_PORT": "8042",
            "OCTA_WORKSPACE_SKIP_UV_SYNC": "1",
            "OCTA_WORKSPACE_SKIP_SEED": "1",
            "OCTA_WORKSPACE_SKIP_QDRANT": "1",
            "OCTA_WORKSPACE_LOG": str(ROOT / "data" / "test-workspace-api-host.log"),
        }
    )
    log_path = Path(env["OCTA_WORKSPACE_LOG"])
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.unlink(missing_ok=True)

    result = subprocess.run(["bash", str(SCRIPT)], cwd=ROOT, env=env, capture_output=True, text=True, check=False)
    assert result.returncode == 1
    assert "localhost" in log_path.read_text(encoding="utf-8")


def test_octa_workspace_api_dev_refuses_non_dev_port() -> None:
    env = os.environ.copy()
    env.update(
        {
            "WORKSPACE_HOST": "127.0.0.1",
            "WORKSPACE_PORT": "9000",
            "OCTA_WORKSPACE_SKIP_UV_SYNC": "1",
            "OCTA_WORKSPACE_SKIP_SEED": "1",
            "OCTA_WORKSPACE_SKIP_QDRANT": "1",
            "OCTA_WORKSPACE_LOG": str(ROOT / "data" / "test-workspace-api-port.log"),
        }
    )
    log_path = Path(env["OCTA_WORKSPACE_LOG"])
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.unlink(missing_ok=True)

    result = subprocess.run(["bash", str(SCRIPT)], cwd=ROOT, env=env, capture_output=True, text=True, check=False)
    assert result.returncode == 1
    assert "8042" in log_path.read_text(encoding="utf-8")
