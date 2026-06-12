<link rel="stylesheet" href="../styles/main.css">

# Faza 3: Application layer i use case'y governance

[← Indeks planowania](README.md) | [Roadmapa](roadmap-draft.md) | [Clean Architecture](../technologies/CleanArchitecture.md) | [DDD](../technologies/DDD.md) | [Python](../technologies/Python.md) | [Pytest](../technologies/Pytest.md) | [PHP → Python](../technologies/PHP-do-Python.md)

Status: draft prywatny

Cel fazy: nauczyć się, jak domenę z Fazy 2 opakować w warstwę aplikacyjną bez wchodzenia jeszcze w FastAPI, bazę danych, LangGraph ani frameworki. To jest etap, w którym zaczynamy myśleć jak backend/AI engineer: domena ma reguły, application wykonuje przypadki użycia.

## Główna idea

Po Fazie 2 mamy czyste modele:

- `Actor`
- `Action`
- `PolicyEvaluation`
- `ApprovalRequest`
- `ApprovalStatus`

W Fazie 3 dodajemy use case'y, które odpowiadają na pytania:

- co ma się wydarzyć, gdy actor chce wykonać action?
- kiedy tworzymy approval request?
- kiedy akcja jest od razu dozwolona?
- kiedy odmawiamy?
- kiedy zapisujemy audit event?
- jakie zależności aplikacja potrzebuje od świata zewnętrznego?

## Zakres techniczny

Publiczne pliki prawdopodobnie powstaną tutaj:

```text
src/secure_agentic_ai/application/
├── __init__.py
├── commands.py
├── ports.py
└── use_cases.py
```

Testy:

```text
tests/unit/application/
├── test_request_action_approval.py
└── test_record_policy_decision.py
```

## Co ćwiczymy w Pythonie

- zwykłe klasy serwisowe,
- dataclasses jako command objects,
- `Protocol` jako porty,
- dependency injection bez frameworka,
- test doubles / fake repositories,
- typowanie zależności,
- rozdział domeny od aplikacji.

## Proponowany model mentalny

```text
adapter/API/CLI/LangGraph node
        |
        v
application use case
        |
        +--> domain policy
        +--> approval repository port
        +--> audit writer port
        |
        v
result object
```

Na tym etapie nadal nie interesuje nas technicznie:

- FastAPI,
- SQLAlchemy,
- PostgreSQL,
- Qdrant,
- LangGraph,
- LangChain,
- Langfuse.

Te narzędzia przyjdą później jako adaptery/infrastruktura.

## Decyzja o async

W Fazie 3 nie robimy jeszcze async.

Application layer ma pozostać prosty i synchroniczny, bo:

- nie wykonuje I/O bezpośrednio,
- nie zna bazy danych,
- nie woła LLM providerów,
- nie zna FastAPI,
- orkiestruje domenę i porty.

Async pojawi się później na granicach systemu:

```text
FastAPI endpoint -> async
SQLAlchemy adapter -> async
Qdrant adapter -> async
LLM provider adapter -> async
LangGraph execution -> async albo async-compatible
```

To oznacza, że use case może dziś wyglądać synchronicznie, a późniejszy adapter może go wywołać z endpointu async bez mieszania domeny z event loopem.

## Checklist

- [ ] 1. Przeczytać obecne pliki domenowe i upewnić się, że rozumiem ich odpowiedzialności.
- [ ] 2. Utworzyć `application/commands.py`.
- [ ] 3. Dodać command object, np. `RequestActionCommand`.
- [ ] 4. Utworzyć `application/ports.py`.
- [ ] 5. Zdefiniować port `ApprovalRequestRepository` jako `Protocol`.
- [ ] 6. Zdefiniować port `AuditWriter` jako `Protocol`.
- [ ] 7. Utworzyć `application/use_cases.py`.
- [ ] 8. Dodać use case `RequestActionUseCase`.
- [ ] 9. Use case powinien wywołać `evaluate_policy(actor, action)`.
- [ ] 10. Dla `ALLOW` zwrócić wynik "allowed".
- [ ] 11. Dla `DENY` zwrócić wynik "denied".
- [ ] 12. Dla `REQUIRE_APPROVAL` utworzyć `ApprovalRequest`.
- [ ] 13. Zapisać `ApprovalRequest` przez repository port.
- [ ] 14. Zapisać audit event przez audit port.
- [ ] 15. Dodać fake repository w testach.
- [ ] 16. Dodać fake audit writer w testach.
- [ ] 17. Przetestować ścieżkę `ALLOW`.
- [ ] 18. Przetestować ścieżkę `DENY`.
- [ ] 19. Przetestować ścieżkę `REQUIRE_APPROVAL`.
- [ ] 20. Uruchomić pełny quality gate:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest
```

## Ważna decyzja architektoniczna

`application` nie powinno wiedzieć, czy approval request trafi kiedyś do:

- pamięci,
- pliku,
- PostgreSQL,
- kolejki,
- LangGraph state,
- FastAPI endpointu.

Warstwa `application` zna tylko port. Konkretna implementacja pojawi się później w `infrastructure` albo `adapters`.

## Oczekiwany rezultat fazy

Po Fazie 3 powinniśmy móc pokazać rekruterowi:

- czystą domenę,
- use case'y niezależne od frameworków,
- testowalną architekturę,
- pierwszą wersję HITL governance flow,
- świadome użycie `Protocol` i dependency inversion w Pythonie.

To będzie dużo mocniejszy sygnał niż szybkie dodanie FastAPI, bo pokaże, że projekt jest projektowany, a nie tylko składany z bibliotek.

## Referencje do PHP

### Application use case vs controller/service

To jest najważniejsza różnica tej fazy: use case nie jest kontrolerem i nie jest miejscem na szczegóły HTTP.

```text
PHP / Symfony-Laravel:
Request -> Controller -> Service -> Repository -> Response

Python / Clean Architecture:
Adapter -> Command -> UseCase -> Domain + Ports -> Result -> Adapter
```

```php
// PHP — controller tłumaczy HTTP na wywołanie serwisu
final class ApprovalController
{
    public function __construct(
        private RequestActionService $service,
    ) {}

    public function __invoke(Request $request): JsonResponse
    {
        $result = $this->service->requestAction(
            actorId: $request->get('actor_id'),
            actionType: $request->get('action_type'),
        );

        return new JsonResponse($result);
    }
}
```

```python
# Python — adapter/API zbuduje command, a use case nie zna HTTP
@dataclass(frozen=True)
class RequestActionCommand:
    actor: Actor
    action: Action


class RequestActionUseCase:
    def execute(self, command: RequestActionCommand) -> RequestActionResult:
        evaluation = evaluate_policy(command.actor, command.action)
        ...
```

**Implikacje dla Python:**

- `application` nie importuje FastAPI.
- `RequestActionCommand` jest wejściem do use case'a, nie requestem HTTP.
- `RequestActionResult` jest wynikiem procesu, nie responsem HTTP.
- Adapter może być później FastAPI, CLI, LangGraph node albo worker.

### Protocol vs PHP interface

`Protocol` w Pythonie jest podobny do interfejsu w PHP, ale działa przez zgodność struktury, nie przez jawne `implements`.

```text
PHP:
Klasa musi jawnie zadeklarować implements RepositoryInterface.

Python:
Klasa nie musi dziedziczyć po Protocol.
Wystarczy, że ma wymagane metody i zgodne typy.
```

```php
// PHP — jawny kontrakt nominalny
interface ApprovalRequestRepositoryInterface
{
    public function save(ApprovalRequest $request): void;
}

final class InMemoryApprovalRequestRepository implements ApprovalRequestRepositoryInterface
{
    /** @var ApprovalRequest[] */
    public array $saved = [];

    public function save(ApprovalRequest $request): void
    {
        $this->saved[] = $request;
    }
}
```

```python
# Python — kontrakt strukturalny przez Protocol
class ApprovalRequestRepository(Protocol):
    def save(self, request: ApprovalRequest) -> None:
        ...


class InMemoryApprovalRequestRepository:
    def __init__(self) -> None:
        self.saved: list[ApprovalRequest] = []

    def save(self, request: ApprovalRequest) -> None:
        self.saved.append(request)
```

**Implikacje dla Python:**

- Implementacja nie musi pisać `implements`.
- `mypy` sprawdzi zgodność, jeśli użyjemy typów konsekwentnie.
- To dobrze pasuje do dependency inversion bez ciężkiego kontenera DI.
- Nazwa metody i sygnatura są ważniejsze niż hierarchia klas.

### Fake repository w testach

W tej fazie lepszy jest mały fake niż rozbudowany mock. Chcemy testować zachowanie use case'a, nie framework mockowania.

```text
PHP/PHPUnit:
Często używasz mocka interfejsu i sprawdzasz, czy metoda została wywołana.

Python/pytest:
Często czytelniejszy jest fake object z listą zapisanych elementów.
Test sprawdza stan fake'a po wykonaniu use case'a.
```

```php
// PHP — typowy mock w PHPUnit
$repo = $this->createMock(ApprovalRequestRepositoryInterface::class);
$repo
    ->expects($this->once())
    ->method('save')
    ->with($this->isInstanceOf(ApprovalRequest::class));
```

```python
# Python — prosty fake, bez frameworka mockowania
class FakeApprovalRequestRepository:
    def __init__(self) -> None:
        self.saved: list[ApprovalRequest] = []

    def save(self, request: ApprovalRequest) -> None:
        self.saved.append(request)


def test_use_case_creates_approval_request() -> None:
    repository = FakeApprovalRequestRepository()
    use_case = RequestActionUseCase(approval_repository=repository)

    result = use_case.execute(command)

    assert result.status is RequestActionStatus.REQUIRES_APPROVAL
    assert len(repository.saved) == 1
```

**Implikacje dla Python:**

- Test jest bliżej zachowania biznesowego.
- Nie wiążemy testu z detalami wywołań, jeśli nie musimy.
- Fake repository działa jak pamięciowy adapter portu.
- To przygotowuje grunt pod późniejszy adapter PostgreSQL.
