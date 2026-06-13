# ADR-005: Masked Secret Values in Domain

**Status:** Accepted  
**Context:** Secrets must never appear in logs, traces, audit events, or prompt context.

**Decision:** `SecretValue` is a frozen dataclass with:
- `.resolve()` returns the actual value (explicit escape hatch)
- `__str__` returns `"****"` (prevents accidental logging)
- `__repr__` returns `SecretValue(name=...)` without the value

**Consequences:**
- `str(sv)` or `f"{sv}"` in any context produces masked output.
- Developers must call `.resolve()` explicitly to get the value.
- Audit events store the secret name, never the value.
- The pattern is simple and testable: `assert "sk-fake" not in str(event.metadata)`.
