# ADR-004: SQLite for Development, PostgreSQL for Production

**Status:** Accepted  
**Context:** The project needs a database that works out of the box for development while supporting production-grade deployment.

**Decision:** Development uses SQLite via `aiosqlite`. The SQLAlchemy async dialect is abstracted, so switching to PostgreSQL requires only changing the connection string.

**Consequences:**
- Zero setup for local development and CI.
- Alembic migrations work with both dialects.
- Docker Compose profile available for PostgreSQL.
- Some PostgreSQL-specific features (e.g., pgvector) deferred until production deployment.
