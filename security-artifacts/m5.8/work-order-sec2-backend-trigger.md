# Work Order — backend trigger for SEC.2 report pull (draft)

**Status:** draft · **Owner:** backend-team → **Consumer:** security-team  
**Blocked until:** SYNC-M16 closed

---

## Context

SEC.2 agents on M1 need a **signal** when new audit reports land (pc-ubuntu daily octa audit, weekly Lynis). Today reports are files + mail; agents can poll, but a lightweight Workspace hook reduces latency.

---

## Proposed scope (backend-team, post-M5.6)

| Option | Description | Effort |
|--------|-------------|--------|
| **A — Poll only** | SEC.2 agent reads `/var/log/octa/` + Knowledge paths on schedule | 0 backend (security-only) |
| **B — Ops endpoint** | `POST /workspace/ops/security/report-ingested` (internal, localhost, optional shared secret) | 1 small PR |
| **C — launchd only** | `scripts/octa-sec-report-notify.sh` invoked from existing audit cron on M1 | 0 API; script in security ownership |

**Recommendation:** start with **A** or **C** for MVP; **B** only if security-team opens WO after SEC.2 spike.

---

## If Option B is approved later

- Auth: `127.0.0.1` only + header `X-Octa-Ops-Token` from Keychain
- Body: `{ "source": "pc-ubuntu|m1", "report_path": "...", "report_type": "octa-daily|lynis" }`
- Response: `{ "queued": true, "review_pending_count": N }`
- Tests: pytest + no E2E UI change
- Docs: `workspace-mvp.md` § ops endpoints

---

## Acceptance (security-team)

- [ ] WO approved with chosen option (A/B/C)
- [ ] No tier-2 auto-exec without HITL
- [ ] SYNC-HITL unchanged

**Contact:** backend-team via triple-track SYNC-API
