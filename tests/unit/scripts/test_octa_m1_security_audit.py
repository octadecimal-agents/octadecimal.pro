"""Tests for octa-m1-security-audit.sh and install script."""

from pathlib import Path

import subprocess

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "scripts" / "octa-m1-security-audit.sh"
INSTALL = ROOT / "scripts" / "install-m1-security-audit-launchd.sh"
SUDOERS = ROOT / "scripts" / "sudoers.d" / "octa-m1-audit"


def test_octa_m1_security_audit_bash_syntax() -> None:
    subprocess.run(["bash", "-n", str(AUDIT)], check=True)
    subprocess.run(["bash", "-n", str(INSTALL)], check=True)


def test_octa_m1_security_audit_mail_defaults() -> None:
    text = AUDIT.read_text()
    assert "security@octadecimal.pl" in text
    assert "admin@octadecimal.pl" in text
    assert "sendmail" in text


def test_sudoers_drop_in_has_logfile() -> None:
    text = SUDOERS.read_text()
    assert 'logfile="/var/log/octa-sudo.log"' in text
