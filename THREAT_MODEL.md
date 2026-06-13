# Threat Model Summary

## Scope

Secure Agentic AI Platform — a governance layer for autonomous agent actions.

## Assets

| Asset | Description |
|-------|-------------|
| Approval decisions | Policy evaluations and human approvals |
| Audit trail | Immutable log of all actions and decisions |
| Agent actions | Any action an autonomous agent attempts |
| Secrets | API keys, database passwords, credentials |
| Knowledge base | Governance documents in the RAG system |

## Threats

### T1 — Prompt Injection (Direct)

**Risk:** An attacker crafts input that bypasses policy or causes unauthorized actions.

**Mitigations:**
- `PatternSafetyChecker` scans action descriptions for injection patterns
- Dangerous content → automatic DENY
- Suspicious content → REQUIRE_APPROVAL (HITL)

**Test:** `tests/integration/test_safety.py`

### T2 — Prompt Injection (Indirect)

**Risk:** Retrieved RAG context contains hidden instructions that alter agent behavior.

**Mitigations:**
- Context from RAG passes through same `SafetyChecker` as direct input
- No distinction between direct and indirect paths

**Test:** `test_safety.py` covers both injection types

### T3 — Secret Leakage via Logs, Traces, or Prompts

**Risk:** Secrets appear in audit events, trace spans, or RAG context.

**Mitigations:**
- `SecretValue.__str__` → `"****"`, `__repr__` → name only
- Audit events log secret name, never value
- Trace spans only include actor/action metadata

**Test:** `test_secrets.py::test_audit_event_does_not_contain_secret_value`

### T4 — Agent Unauthorized Secret Resolution

**Risk:** An agent resolves a secret without authorization.

**Mitigations:**
- Policy: `AGENT + RESOLVE_SECRET → DENY` (hard-coded in `evaluate_policy`)
- High-risk actions require human approval
- All resolution attempts are audited

**Test:** `test_secrets.py::test_use_case_denies_agent`

### T5 — Policy Bypass via MCP Tools

**Risk:** An agent calls a tool that bypasses the policy engine.

**Mitigations:**
- MCP tool handler routes every call through `RequestActionUseCase`
- `read_document` is read-only, LOW risk
- `ToolExecutionError` surfaced for denied calls

**Test:** `test_mcp.py::test_handler_denied_when_use_case_denies`

### T6 — Insecure State Transitions

**Risk:** Approval request moves to an invalid status.

**Mitigations:**
- `ApprovalRequest.transition_to()` validates against allowed transitions
- `InvalidApprovalTransitionError` raised on violations

**Test:** `test_approvals.py`

### T7 — Audit Tampering

**Risk:** Audit events are modified or deleted.

**Mitigations:**
- `AuditEvent` is a frozen dataclass (immutable)
- SQLAlchemy layer writes events (current limitation: no append-only enforcement at DB level)
- Future: DB triggers / PostgreSQL row-level security

## Out of Scope (Current Phase)

- ML-based prompt injection classifiers (pattern-based only)
- Full database audit immutability (append-only tables)
- Network-level security (TLS, API authentication)
- Container security (Docker hardening)
