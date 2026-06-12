<link rel="stylesheet" href="../styles/main.css">

# Faza 2: Domain Model For Governance

[← Indeks planowania](README.md) | [Roadmapa](roadmap-draft.md) | [Clean Architecture](../technologies/CleanArchitecture.md) | [DDD](../technologies/DDD.md) | [HITL](../technologies/HITL.md) | [RBAC](../technologies/RBAC.md)

Status: prywatna instrukcja robocza

Cel fazy: zbudować pierwszy realny model domenowy platformy bez frameworków, bazy danych i LLM. To ma być czysty Python, który opisuje governance dla agentic AI: aktorów, akcje, requesty approval, decyzje, przejścia stanów i audit events.

## Dlaczego ta faza jest ważna

To jest pierwszy moment, w którym projekt zaczyna mówić:

> Nie buduję tylko integracji LLM. Buduję system z regułami, stanem, bezpieczeństwem i testami.

FastAPI, LangGraph i PostgreSQL przyjdą później. Teraz chcemy mieć domenę, którą da się zrozumieć i przetestować bez infrastruktury.

## Zasada pracy

W tej fazie nie importujemy:

- FastAPI,
- SQLAlchemy,
- LangChain,
- LangGraph,
- Pydantic,
- klientów LLM,
- Bitwardena.

Używamy standardowej biblioteki Pythona:

- `dataclasses`,
- `enum`,
- `datetime`,
- `uuid`,
- `typing`.

Pydantic dodamy później na granicach API. Domenę najpierw budujemy jako czysty Python.

## Oczekiwany efekt końcowy

Powinny istnieć modele i testy dla:

- `Actor`,
- `Action`,
- `Capability`,
- `ApprovalRequest`,
- `ApprovalDecision`,
- `ApprovalStatus`,
- `AuditEvent`,
- reguł przejść stanów,
- przypadków dozwolonych i zabronionych.

Pełne checks:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy .
```

## Proponowana struktura

```text
src/secure_agentic_ai/domain/
├── __init__.py
├── actors.py
├── approvals.py
├── audit.py
├── policies.py
└── errors.py

tests/unit/domain/
├── test_approval_request.py
├── test_approval_decisions.py
└── test_audit_event.py
```

## Kluczowy model mentalny

```text
Actor requests Action
Policy decides whether Action is allowed directly or requires approval
ApprovalRequest tracks human decision state
AuditEvent records what happened
```

Nie robimy jeszcze policy engine w pełnym sensie. Robimy minimalny język domenowy, na którym później oprzemy use case'y.

## Checklist

### 1. Start z aktualnego main

Status: [x]

Komendy:

```bash
git switch main
git pull --ff-only origin main
git status --short --branch
```

Oczekiwane:

```text
## main...origin/main
```

### 2. Utwórz branch Fazy 2

Status: [x]

Komenda:

```bash
git switch -c feature/domain-governance-model
```

Cel:

Oddzielić model domenowy od main i utrzymać czytelną historię.

### 3. Uruchom baseline checks

Status: [x]

Komendy:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy .
```

Cel:

Upewnić się, że zaczynamy z działającego punktu.

### 4. Dodaj plik błędów domenowych

Status: [x]

Plik:

```text
src/secure_agentic_ai/domain/errors.py
```

Idea:

Zamiast rzucać wszędzie generyczne `ValueError`, tworzymy własny typ błędu domenowego.

Proponowany minimalny model:

```python
class DomainError(Exception):
    """Base class for domain rule violations."""
```

Cel wiedzy:

Zrozumieć, że wyjątek domenowy opisuje naruszenie reguły systemu, a nie błąd techniczny.

### 5. Dodaj model aktora i capability

Status: [ ]

Plik:

```text
src/secure_agentic_ai/domain/actors.py
```

Pojęcia:

- `ActorId`,
- `Capability`,
- `Actor`.

Decyzja do przemyślenia:

Czy `ActorId` ma być zwykłym `str`, typem przez `NewType`, czy value object?

Rekomendacja na start:

- użyć `dataclass(frozen=True)` dla `Actor`,
- użyć `Enum` dla `Capability`,
- zostawić `actor_id` jako `str` albo prosty value object, bez przesady.

Przykładowe capability:

```text
REQUEST_APPROVAL
READ_AUDIT
APPROVE_ACTION
EXECUTE_APPROVED_ACTION
```

Cel wiedzy:

Zrozumieć różnicę między rolą, capability i konkretnym aktorem.

### 6. Dodaj model akcji

Status: [ ]

Plik:

```text
src/secure_agentic_ai/domain/policies.py
```

Pojęcia:

- `ActionType`,
- `ActionRisk`,
- `Action`.

Przykładowe typy akcji:

```text
READ_DATA
WRITE_FILE
RUN_TOOL
RESOLVE_SECRET
CALL_EXTERNAL_API
```

Przykładowe poziomy ryzyka:

```text
LOW
MEDIUM
HIGH
```

Cel wiedzy:

Zrozumieć, że system nie ocenia tylko "czy aktor może", ale też "jak ryzykowna jest akcja".

### 7. Dodaj approval status

Status: [ ]

Plik:

```text
src/secure_agentic_ai/domain/approvals.py
```

Statusy:

```text
PENDING
APPROVED
REJECTED
EXECUTED
FAILED
```

Cel wiedzy:

Statusy workflow powinny być jawne i ograniczone, a nie wpisywane jako luźne stringi.

### 8. Dodaj `ApprovalRequest`

Status: [ ]

Plik:

```text
src/secure_agentic_ai/domain/approvals.py
```

Minimalne pola:

- `id`,
- `actor_id`,
- `action_type`,
- `status`,
- `reason`,
- `created_at`,
- `decided_at`.

Minimalne metody:

- `approve()`,
- `reject()`,
- `mark_executed()`,
- `mark_failed()`.

Reguły:

- tylko `PENDING` można zatwierdzić,
- tylko `PENDING` można odrzucić,
- tylko `APPROVED` można oznaczyć jako executed,
- tylko `APPROVED` można oznaczyć jako failed,
- po decyzji powinno pojawić się `decided_at`.

Cel wiedzy:

To jest pierwszy prawdziwy aggregate-like model. Reguły stanu są w modelu, nie w endpointach.

### 9. Testy przejść dozwolonych

Status: [ ]

Plik:

```text
tests/unit/domain/test_approval_request.py
```

Testy:

- nowy request ma status `PENDING`,
- `approve()` zmienia status na `APPROVED`,
- `reject()` zmienia status na `REJECTED`,
- `mark_executed()` działa po approve,
- `mark_failed()` działa po approve.

Cel wiedzy:

Testujemy zachowanie domeny bez żadnego API.

### 10. Testy przejść zabronionych

Status: [ ]

Plik:

```text
tests/unit/domain/test_approval_decisions.py
```

Testy:

- nie można approve po reject,
- nie można reject po approve,
- nie można execute bez approve,
- nie można failed bez approve,
- ponowna decyzja rzuca `DomainError`.

Cel wiedzy:

Dla security ważniejsze są często ścieżki denied niż happy path.

### 11. Dodaj `AuditEvent`

Status: [ ]

Plik:

```text
src/secure_agentic_ai/domain/audit.py
```

Minimalne pola:

- `id`,
- `event_type`,
- `actor_id`,
- `action_type`,
- `request_id`,
- `timestamp`,
- `metadata`.

Przykładowe event types:

```text
APPROVAL_REQUESTED
APPROVAL_APPROVED
APPROVAL_REJECTED
ACTION_EXECUTED
ACTION_FAILED
POLICY_DENIED
```

Cel wiedzy:

Audit event nie jest logiem tekstowym. To strukturalny fakt o tym, co wydarzyło się w systemie.

### 12. Test `AuditEvent`

Status: [ ]

Plik:

```text
tests/unit/domain/test_audit_event.py
```

Testy:

- event ma timestamp,
- event ma typ,
- event może zawierać metadata,
- metadata domyślnie nie jest współdzielona między instancjami.

Cel wiedzy:

Uważać na mutable defaults w Pythonie. To klasyczna pułapka.

### 13. Eksporty z pakietu domeny

Status: [ ]

Plik:

```text
src/secure_agentic_ai/domain/__init__.py
```

Cel:

Ułatwić czytelne importy w testach.

Przykład:

```python
from secure_agentic_ai.domain import ApprovalRequest, ApprovalStatus
```

Uwaga:

Nie eksportuj wszystkiego bezmyślnie. Eksporty w `__init__.py` tworzą publiczny interfejs modułu.

### 14. Uruchom testy

Status: [ ]

Komenda:

```bash
uv run pytest
```

Cel:

Sprawdzić, czy domena działa zgodnie z regułami.

### 15. Uruchom Ruff

Status: [ ]

Komendy:

```bash
uv run ruff check .
uv run ruff format --check .
```

Jeśli format failuje:

```bash
uv run ruff format .
uv run ruff format --check .
```

### 16. Uruchom mypy

Status: [ ]

Komenda:

```bash
uv run mypy .
```

Cel:

Sprawdzić, czy typy domenowe są spójne.

### 17. Zaktualizuj prywatne notatki wiedzy

Status: [ ]

Opcjonalne pliki:

- `.dev/technologies/Python.md`,
- `.dev/technologies/DDD.md`,
- `.dev/technologies/CleanArchitecture.md`,
- `.dev/explanations/notes.md`.

Tematy:

- `dataclass(frozen=True)`,
- `Enum`,
- mutable defaults,
- domain exceptions,
- status transitions,
- aggregate-like model.

### 18. Sprawdź diff przed commitem

Status: [ ]

Komendy:

```bash
git status --short
git diff --stat
```

Oczekiwane:

- nowe pliki w `src/secure_agentic_ai/domain/`,
- nowe testy w `tests/unit/domain/`,
- ewentualnie zmieniony `src/secure_agentic_ai/domain/__init__.py`.

Nie powinno wejść:

- `.dev/`,
- `.history/`,
- `.DS_Store`,
- cache,
- pliki eksperymentalne.

### 19. Commit

Status: [ ]

Proponowany commit:

```bash
git add src/secure_agentic_ai/domain tests/unit/domain
git commit -m "feat(domain): add governance model"
```

Jeśli zmian wyjdzie dużo, można podzielić:

```text
feat(domain): add actors and action policies
feat(domain): add approval request state model
feat(domain): add audit event model
```

Decyzję podejmiemy po diffie.

### 20. Push i PR

Status: [ ]

Komendy:

```bash
git push -u origin feature/domain-governance-model
```

PR powinien opisywać:

- jakie modele domenowe dodano,
- jakie reguły są testowane,
- że nie ma jeszcze FastAPI/bazy/LLM,
- że to świadomy domain-first slice.

## Pytania kontrolne po fazie

Po tej fazie powinieneś umieć odpowiedzieć:

1. Dlaczego domena nie importuje FastAPI?
2. Czym różni się status workflow od zwykłego stringa?
3. Dlaczego denied transitions są tak ważne?
4. Po co własny `DomainError`?
5. Czym jest audit event i dlaczego nie wystarczy zwykły log?
6. Czym jest mutable default w Pythonie?
7. Czy `ApprovalRequest` jest agregatem w sensie DDD? Jeśli tak, w jakim uproszczonym sensie?
8. Jak ten model później podepniemy pod FastAPI?
9. Jak ten model później podepniemy pod LangGraph?

## Decyzje odłożone

Na tym etapie nie decydujemy jeszcze:

- jak wygląda persistence,
- czy ID będą UUID czy ULID w finalnej wersji,
- jak wygląda pełny policy engine,
- jak dokładnie LangGraph będzie mapować stan,
- jak wygląda API,
- jak wygląda UI approval console.
