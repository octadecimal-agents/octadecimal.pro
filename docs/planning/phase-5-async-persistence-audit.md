<link rel="stylesheet" href="../styles/main.css">

# Faza 5: Async Persistence And Audit Trail

[← Indeks planowania](README.md) | [Roadmapa](roadmap-draft.md) | [SQLAlchemy](../technologies/SQLAlchemy.md) | [Alembic](../technologies/Alembic.md) | [PostgreSQL](../technologies/PostgreSQL.md) | [Docker](../technologies/Docker.md) | [PHP → Python](../technologies/PHP-do-Python.md)

Status: draft prywatny

Cel fazy: zamienić pamięciowe adaptery na trwałą persystencję w PostgreSQL i dodać realny audit trail.

## Główna idea

Application zna porty. Infrastructure dostarcza implementacje:

```text
ApprovalRequestRepository Protocol -> SQLAlchemyApprovalRequestRepository
AuditWriter Protocol -> SQLAlchemyAuditWriter albo JsonlAuditWriter
```

## Zakres techniczny

```text
src/secure_agentic_ai/infrastructure/persistence/
├── __init__.py
├── models.py
├── session.py
└── approval_repository.py

src/secure_agentic_ai/infrastructure/audit/
└── audit_writer.py
```

## Co ćwiczymy w Pythonie

- async SQLAlchemy 2.0,
- session lifecycle,
- transakcje,
- Alembic migrations,
- integration tests,
- mapowanie domain model <-> database row.

## Czego nie robimy w tej fazie

- LangGraph,
- RAG,
- LLM,
- MCP,
- production-grade observability,
- pełnego modelu multi-tenant.

## Checklist

- [ ] 1. Spike async SQLAlchemy: engine, session, transakcja, rollback.
- [ ] 2. Dodać Docker Compose z PostgreSQL.
- [ ] 3. Dodać SQLAlchemy models.
- [ ] 4. Dodać Alembic.
- [ ] 5. Dodać migrację approval requests.
- [ ] 6. Dodać migrację audit events.
- [ ] 7. Zaimplementować repository adapter.
- [ ] 8. Zaimplementować audit writer.
- [ ] 9. Podmienić dependencies FastAPI na adaptery infrastruktury.
- [ ] 10. Dodać integration tests.
- [ ] 11. Sprawdzić transakcje i rollback.
- [ ] 12. Uruchomić quality gate.

## Referencje do PHP

### SQLAlchemy session vs Doctrine EntityManager

Podobieństwo jest kuszące, ale lifecycle jest inny.

```text
PHP:
EntityManager żyje zwykle w cyklu requestu.

Python/ASGI:
Proces żyje długo, engine/pool żyją długo, session powinna być krótka.
```

```php
// PHP — typowo request-scoped EntityManager
$approval = new ApprovalRequest(...);
$entityManager->persist($approval);
$entityManager->flush();
```

```python
# Python — engine globalny, session krótka
engine = create_async_engine(dsn)
Session = async_sessionmaker(engine, expire_on_commit=False)

async with Session() as session:
    session.add(row)
    await session.commit()
```

**Implikacje dla Python:**

- Engine tworzysz raz.
- Session tworzysz na krótki zakres pracy.
- Use case nie powinien znać session.
- Repository adapter zarządza mapowaniem i persystencją.

### Alembic vs Doctrine migrations

```text
PHP:
Doctrine migrations wersjonują zmiany schematu.

Python:
Alembic robi to samo dla SQLAlchemy.
```

```php
// PHP — migracja Doctrine
public function up(Schema $schema): void
{
    $this->addSql('CREATE TABLE approval_request (...)');
}
```

```python
# Python — migracja Alembic
def upgrade() -> None:
    op.create_table(
        "approval_request",
        sa.Column("id", sa.String(), primary_key=True),
    )
```

**Implikacje dla Python:**

- Migracje są częścią kodu, nie ręcznym SQL-em w notatniku.
- Test od zera powinien umieć postawić schemat.
- Publiczne portfolio z migracjami wygląda dużo dojrzalej niż tylko modele ORM.

## Oczekiwany rezultat fazy

Approval i audit mają trwały zapis. System ma pierwszy realny ślad audytowy, a application nadal zależy tylko od portów.
