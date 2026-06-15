import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = (
    ROOT / "scripts" / "octa",
    ROOT / "scripts" / "octa-workspace-open.sh",
    ROOT / "scripts" / "octa-m1-smoke-check.sh",
)


def test_octa_m5_6_scripts_have_valid_bash_syntax() -> None:
    for path in (
        *SCRIPTS,
        ROOT / "scripts" / "octa-calendar-sync-m1.sh",
        ROOT / "scripts" / "install-m1-calendar-automation.sh",
        ROOT / "scripts" / "install-calendar-sync-m1-launchd.sh",
    ):
        result = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True, check=False)
        assert result.returncode == 0, f"{path.name}: {result.stderr}"


def test_octa_cli_dispatches_workspace_smoke_help() -> None:
    result = subprocess.run(
        ["bash", str(ROOT / "scripts" / "octa"), "workspace", "smoke", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "--remote" in result.stdout


def test_octa_cli_unknown_command_exits_nonzero() -> None:
    result = subprocess.run(
        ["bash", str(ROOT / "scripts" / "octa"), "unknown"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
