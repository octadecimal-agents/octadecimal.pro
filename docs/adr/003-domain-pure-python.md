# ADR-003: Domain Is Pure Python

**Status:** Accepted  
**Context:** The domain layer should be framework-agnostic, testable without infrastructure, and represent business concepts in plain code.

**Decision:** Domain uses only `dataclasses`, `StrEnum`, and plain Python. No Pydantic, SQLAlchemy, FastAPI, or any framework import crosses into domain.

**Consequences:**
- Domain can be tested without any infrastructure (pure unit tests).
- Domain models are lightweight and focused on behavior (e.g., `ApprovalRequest.transition_to()`).
- Adapters handle serialization, persistence, and I/O.
- `dataclass(frozen=True)` enforces immutability for value objects and events.
