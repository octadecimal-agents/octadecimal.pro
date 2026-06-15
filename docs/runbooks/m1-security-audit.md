<link rel="stylesheet" href="../styles/main.css">

# Runbook — M1 security audit (email)

[← M1 server mode](workspace-m1-server-mode.md) · [Knowledge sync M1](knowledge-sync-m1.md)

**Goal:** daily audit of M1 server posture + **on-demand audit after sudo use** — email report to `security@octadecimal.pl` from `admin@octadecimal.pl`.

**Runs on:** M1 only (LaunchDaemons as root).

---

## 1. What it checks

| Area | Check |
|------|--------|
| Workspace | `127.0.0.1:8042/health`, LaunchDaemon state |
| Network | LAN must **not** reach `:8042`; list non-localhost listeners |
| Power | `SleepDisabled`, headless readiness |
| Firewall | Application firewall enabled |
| SSH | Remote Login status |
| Disk | Free space on `/` |
| Knowledge | Last M5 rsync marker |
| Sudo | Tail of `/var/log/octa-sudo.log` |

Warnings are counted in subject line: `[M1 Audit/daily] … — 2 warning(s)`.

---

## 2. Triggers

| Trigger | Mechanism |
|---------|-----------|
| **daily** | LaunchDaemon `pl.octadecimal.m1-security-audit-daily` at **06:00** local |
| **sudo** | `WatchPaths` on `/var/log/octa-sudo.log` (max once per **300 s**) |
| **manual** | `./scripts/octa-m1-security-audit.sh` |

Sudo logging: `/etc/sudoers.d/octa-m1-audit` → `Defaults logfile="/var/log/octa-sudo.log"`.

---

## 3. Install (M1 Admin + sudo)

```bash
cd /Users/ceo/Developer/Repositories/octadecimal-agents/octadecimal.pro
chmod +x scripts/octa-m1-security-audit.sh scripts/install-m1-security-audit-launchd.sh
sudo ./scripts/install-m1-security-audit-launchd.sh
```

**Requires:** outbound mail via system `sendmail` (Mail account `admin@octadecimal.pl` configured on M1).

Test pipeline:

```bash
sudo ./scripts/octa-m1-security-audit.sh --test-email
sudo ./scripts/octa-m1-security-audit.sh --report-only
```

Uninstall:

```bash
sudo ./scripts/install-m1-security-audit-launchd.sh --uninstall
```

---

## 4. Logs and reports

| Path | Content |
|------|---------|
| `/var/log/octa/m1-security-audit.log` | Audit run log |
| `/var/log/octa/m1-audit-reports/*.txt` | Archived reports |
| `/var/log/octa-sudo.log` | Sudo session log |
| `/var/log/octa/m1-security-audit-daily.*.log` | launchd stdout/stderr |
| `/var/log/octa/m1-sudo-audit-watch.*.log` | sudo watcher launchd |

---

## 5. Environment overrides

| Variable | Default |
|----------|---------|
| `OCTA_M1_AUDIT_MAIL_TO` | `security@octadecimal.pl` |
| `OCTA_M1_AUDIT_MAIL_FROM` | `admin@octadecimal.pl` |
| `OCTA_M1_AUDIT_TRIGGER` | `manual` / `daily` / `sudo` |
| `OCTA_M1_AUDIT_SKIP_MAIL` | `1` with `--report-only` |

---

## 6. Troubleshooting

| Symptom | Fix |
|---------|-----|
| No email | `sudo ./scripts/octa-m1-security-audit.sh --test-email`; check Mail/sendmail relay |
| Sudo audit never fires | `sudo tail /var/log/octa-sudo.log` after `sudo ls`; verify WatchPaths job loaded |
| `visudo` failed on install | Fix `scripts/sudoers.d/octa-m1-audit`; re-run installer |
| Mail spam on busy sudo | Increase `ThrottleInterval` in sudo-watch plist (default 300s) |

---

## 7. Knowledge (PL)

`Knowledge/02-6-Rooms-Model/Operacje/m1/Administrator-M1.md` §6.4
