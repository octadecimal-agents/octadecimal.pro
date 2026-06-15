<link rel="stylesheet" href="../styles/main.css">

# Runbook — PC Ubuntu security audit (email)

[← PC Ubuntu server](../../Knowledge/01-Base-Point/pro/servers/pc-ubuntu/README.md) · [M1 audit](m1-security-audit.md)

**Goal:** daily security posture report + audit on **sudo use** — email to `security@octadecimal.pl`.

**Replaces:** legacy `/usr/local/bin/system-monitor.sh` (temperature/load-only alerts).

---

## 1. Triggers

| Trigger | Mechanism |
|---------|-----------|
| **daily** | `/etc/cron.d/octa-pc-ubuntu-security-audit` — 06:00 UTC |
| **sudo** | cron every 5 min → `octa-pc-ubuntu-sudo-audit-watch.sh` reads `/var/log/octa-sudo.log` |
| **manual** | `/usr/local/bin/octa-pc-ubuntu-security-audit.sh` |

---

## 2. Install (pc-ubuntu root)

From repo on server (or after rsync from M5):

```bash
cd /path/to/octadecimal.pro
chmod +x scripts/install-pc-ubuntu-security-audit.sh scripts/octa-pc-ubuntu-security-audit.sh
sudo bash scripts/install-pc-ubuntu-security-audit.sh
sudo /usr/local/bin/octa-pc-ubuntu-security-audit.sh --test-email
```

Uninstall:

```bash
sudo ./scripts/install-pc-ubuntu-security-audit.sh --uninstall
```

---

## 3. Report contents

- Uptime, load, CPU temperature (legacy thresholds)
- RAM/swap, disk, zombies
- Docker containers (running/unhealthy)
- Local health probes (Qdrant, n8n, Twenty, Workspace if present)
- Listening ports, UFW, SSH failures
- Pending security apt updates
- Recent sudo log tail
- Warning count in subject line

---

## 4. Logs

| Path | Content |
|------|---------|
| `/var/log/octa/pc-ubuntu-security-audit.log` | Audit runs |
| `/var/log/octa/pc-ubuntu-audit-reports/` | Archived reports |
| `/var/log/octa-sudo.log` | Sudo sessions |
| `/var/log/octa/pc-ubuntu-audit-cron.log` | Daily cron stdout |
| `/var/log/octa/pc-ubuntu-sudo-watch-cron.log` | Sudo watch cron |

---

## 5. Legacy compatibility

`/usr/local/bin/system-monitor.sh` → symlink to `octa-pc-ubuntu-security-audit.sh`.

For alert-only behaviour (old script):

```bash
/usr/local/bin/octa-pc-ubuntu-security-audit.sh --legacy-alert-only
```

---

## 6. Deploy from M5

```bash
rsync -az octadecimal.pro/scripts/ pc-ubuntu:~/octa-security-audit/scripts/
ssh pc-ubuntu 'cd ~/octa-security-audit/scripts/.. && sudo ./scripts/install-pc-ubuntu-security-audit.sh'
```

Or via Bitwarden sudo: `tools/sudo/pc-ubuntu-run.sh "bash ~/octa-security-audit/scripts/install-pc-ubuntu-security-audit.sh"`
