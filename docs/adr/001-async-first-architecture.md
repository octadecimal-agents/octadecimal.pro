# ADR-001: Async-First Architecture

**Status:** Accepted  
**Context:** The platform needs to support I/O-bound operations (DB, LLM, external APIs) without blocking.

**Decision:** All ports, use cases, and infrastructure are async-first. The domain layer remains synchronous.

**Consequences:**
- FastAPI naturally supports async endpoints.
- SQLAlchemy async engine enables connection pooling in a long-running process.
- LangGraph's async API aligns with the rest of the stack.
- Testing requires `pytest-asyncio` for all integration tests.

**Tradeoff:** Slightly more complex test setup vs. synchronous. Worth it for realistic async behavior.
