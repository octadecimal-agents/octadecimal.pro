#!/usr/bin/env bash
# M5.6 — daily unattended smoke from M5 → M1. Appends machine log; optional markdown sync.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SSH_HOST="${OCTA_M1_SSH_HOST:-m1-ceo}"
JSONL_LOG="${OCTA_SMOKE_JSONL:-${HOME}/.octa/logs/m5-6-m1-smoke.jsonl}"
TEXT_LOG="${OCTA_SMOKE_TEXT_LOG:-${HOME}/.octa/logs/m5-6-m1-smoke.log}"
SMOKE_DOC="${REPO_ROOT}/docs/runbooks/workspace-m5-6-smoke-log.md"
UPDATE_DOC="${OCTA_SMOKE_UPDATE_DOC:-0}"

mkdir -p "$(dirname "${JSONL_LOG}")"

DATE_LOCAL="$(date +%Y-%m-%d)"
TIME_LOCAL="$(date +%H:%M)"
TS_ISO="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

tmp_json="$(mktemp)"
trap 'rm -f "${tmp_json}"' EXIT

set +e
"${REPO_ROOT}/scripts/octa-m1-smoke-check.sh" --remote "${SSH_HOST}" --json >"${tmp_json}" 2>/dev/null
smoke_rc=$?
set -e

if [[ ! -s "${tmp_json}" ]]; then
  echo "[${DATE_LOCAL} ${TIME_LOCAL}] FAIL — smoke produced no JSON (ssh ${SSH_HOST}?)" | tee -a "${TEXT_LOG}"
  exit 1
fi

python3 - <<PY
import json
from pathlib import Path

repo = Path("${REPO_ROOT}")
src = Path("${tmp_json}")
out_jsonl = Path("${JSONL_LOG}")
out_text = Path("${TEXT_LOG}")

body = json.loads(src.read_text())
entry = {
    "logged_at": "${TS_ISO}",
    "date_local": "${DATE_LOCAL}",
    "time_local": "${TIME_LOCAL}",
    "ssh_host": "${SSH_HOST}",
    "exit_ok": ${smoke_rc} == 0,
    **body,
}
out_jsonl.parent.mkdir(parents=True, exist_ok=True)
with out_jsonl.open("a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

failures = body.get("failures", 0)
warnings = body.get("warnings", 0)
health = body.get("health") or {}
cal = health.get("calendar_source", "?")
status = health.get("status", "?")
if failures:
    result = "FAIL"
elif warnings:
    result = "PASS+w"
else:
    result = "PASS"
notes = []
if cal.startswith("fixture"):
    notes.append("calendar permission pending on M1")
line = f"[{entry['date_local']} {entry['time_local']}] {result} status={status} calendar={cal} failures={failures} warnings={warnings}"
if notes:
    line += " — " + "; ".join(notes)
out_text.parent.mkdir(parents=True, exist_ok=True)
with out_text.open("a", encoding="utf-8") as f:
    f.write(line + "\n")
print(line)
PY

if [[ "${UPDATE_DOC}" == "1" && -f "${SMOKE_DOC}" ]]; then
  python3 - <<PY
import json
import re
from pathlib import Path

doc = Path("${SMOKE_DOC}")
jsonl = Path("${JSONL_LOG}")
if not jsonl.exists():
    raise SystemExit(0)

by_date = {}
for line in jsonl.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    e = json.loads(line)
    d = e.get("date_local")
    if d:
        by_date[d] = e

days = sorted(by_date.keys())[-3:]
if not days:
    raise SystemExit(0)

rows = []
for i, d in enumerate(days, start=1):
    e = by_date[d]
    h = e.get("health") or {}
    cal = h.get("calendar_source", "?")
    failures = e.get("failures", 0)
    warnings = e.get("warnings", 0)
    if failures:
        res = "FAIL"
    elif warnings:
        res = "PASS+w"
    else:
        res = "PASS"
    note = "auto M5→M1"
    if cal.startswith("fixture"):
        note += "; calendar pending"
    rows.append(f"| {i} | {d} | {res} | {cal} | {note} |")

text = doc.read_text(encoding="utf-8")
block = "\n".join(rows) + "\n"
pattern = r"(\| Day \| Date \| Result \| calendar_source \| Notes \|\n\|-----\|------\|--------\|-----------------\|-------\|\n)(?:\| [^\n]+\n)*"
repl = r"\1" + block
new_text, n = re.subn(pattern, repl, text, count=1)
if n:
    doc.write_text(new_text, encoding="utf-8")
    print(f"Updated smoke log table in {doc.name} ({len(days)} day(s))")
PY
fi

exit "${smoke_rc}"
