# ADR-002: Protocol Ports Over Abstract Classes

**Status:** Accepted  
**Context:** The application layer needs to define interfaces that infrastructure implements, without coupling to any particular framework.

**Decision:** Use `typing.Protocol` for all ports instead of ABCs or abstract base classes.

**Consequences:**
- Structural subtyping: any object with matching methods satisfies the protocol.
- No explicit inheritance required in adapters.
- Easy to create fakes in tests without inheriting from a base.
- Protocols are lightweight — just method signatures.

**Example:**
```python
class AuditWriter(Protocol):
    async def record(self, event: AuditEvent) -> None: ...

class SqlAlchemyAuditWriter:
    async def record(self, event: AuditEvent) -> None:
        ...  # No "implements AuditWriter" needed
```
