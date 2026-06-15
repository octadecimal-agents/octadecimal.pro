"""Tests for PC Ubuntu security audit scripts."""

from pathlib import Path

import subprocess

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "scripts" / "octa-pc-ubuntu-security-audit.sh"
WATCH = ROOT / "scripts" / "octa-pc-ubuntu-sudo-audit-watch.sh"
INSTALL = ROOT / "scripts" / "install-pc-ubuntu-security-audit.sh"


def test_pc_ubuntu_security_audit_bash_syntax() -> None:
    subprocess.run(["bash", "-n", str(AUDIT)], check=True)
    subprocess.run(["bash", "-n", str(WATCH)], check=True)
    subprocess.run(["bash", "-n", str(INSTALL)], check=True)


def test_pc_ubuntu_security_audit_mail_target() -> None:
    text = AUDIT.read_text()
    assert "security@octadecimal.pl" in text
    assert "sendmail" in text
