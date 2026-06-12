<link rel="stylesheet" href="../styles/main.css">

# Faza 4: FastAPI Async Application Boundary

[← Indeks planowania](README.md) | [Roadmapa](roadmap-draft.md) | [FastAPI](../technologies/FastAPI.md) | [Pydantic](../technologies/Pydantic.md) | [Python](../technologies/Python.md) | [PHP → Python](../technologies/PHP-do-Python.md)

Status: draft prywatny

Cel fazy: wystawić pierwszy HTTP API boundary jako cienki adapter nad warstwą `application`, bez przenoszenia logiki biznesowej do endpointów.

## Główna idea

Po Fazie 3 mamy use case'y, commands, results i porty. Faza 4 ma dodać wejście HTTP:

```text
HTTP request -> Pydantic schema -> Command -> UseCase -> Result -> HTTP response
```

FastAPI jest adapterem. Nie jest miejscem, gdzie podejmujemy decyzje policy.

## Zakres techniczny

Publiczne pliki prawdopodobnie powstaną tutaj:

```text
src/secure_agentic_ai/adapters/api/
├── __init__.py
├── app.py
├── dependencies.py
├── routes.py
└── schemas.py
```

Testy:

```text
tests/unit/adapters/api/
└── test_approval_routes.py
```

## Co ćwiczymy w Pythonie

- async endpointy,
- Pydantic v2 models,
- mapowanie schema -> command,
- mapowanie result -> response,
- dependency injection w FastAPI,
- testowanie API przez `httpx` albo `TestClient`.

## Pydantic w tej fazie

### Po co nam Pydantic

Pydantic w Fazie 4 jest warstwą walidacji i serializacji na granicy HTTP.

Nie zastępuje domeny.

Nie zastępuje use case'ów.

Nie zastępuje policy.

Jego rola:

```text
JSON z HTTP -> Pydantic request schema -> application command
application result -> Pydantic response schema -> JSON response
```

Pydantic odpowiada na pytania:

- czy request ma wymagane pola?
- czy pola mają poprawne typy?
- czy wartości mieszczą się w prostych ograniczeniach?
- jak wygenerować OpenAPI schema?
- jak bezpiecznie zamienić Python object na JSON?

Pydantic nie powinien odpowiadać na pytania:

- czy agent może wykonać akcję?
- czy akcja wymaga approval?
- czy approval transition jest legalne?
- czy audit event powinien powstać?

Te pytania zostają w domain/application.

### Dataclass vs Pydantic w naszym projekcie

Robocza zasada:

```text
domain dataclass:
  modeluje pojęcia biznesowe i reguły

application dataclass:
  modeluje commands/results między adapterem i use case'em

Pydantic BaseModel:
  modeluje dane wejścia/wyjścia na granicy systemu
```

Przykład:

```text
HTTP JSON:
  {"request_id": "req-001", "actor_id": "agent-001", ...}

Pydantic:
  RequestActionPayload

Application:
  RequestActionCommand

Domain:
  Actor, Action
```

### Minimalny request schema

To może trafić do `src/secure_agentic_ai/adapters/api/schemas.py`.

```python
from pydantic import BaseModel, Field

from secure_agentic_ai.application.commands import RequestActionCommand
from secure_agentic_ai.domain.actors import Actor, ActorType
from secure_agentic_ai.domain.policies import Action, ActionType, RiskLevel


class RequestActionPayload(BaseModel):
    request_id: str = Field(min_length=1)
    actor_id: str = Field(min_length=1)
    actor_type: ActorType
    actor_display_name: str = Field(min_length=1)
    action_type: ActionType
    risk_level: RiskLevel
    action_description: str = Field(min_length=1)

    def to_command(self) -> RequestActionCommand:
        return RequestActionCommand(
            request_id=self.request_id,
            actor=Actor(
                actor_id=self.actor_id,
                actor_type=self.actor_type,
                display_name=self.actor_display_name,
            ),
            action=Action(
                action_type=self.action_type,
                risk_level=self.risk_level,
                description=self.action_description,
            ),
        )
```

Co tu się dzieje:

- `BaseModel` daje walidację i serializację.
- `Field(min_length=1)` odrzuci pusty string.
- `ActorType`, `ActionType`, `RiskLevel` są enumami domenowymi.
- `to_command()` jest mapowaniem z API schema do application command.

### Minimalny response schema

```python
from pydantic import BaseModel

from secure_agentic_ai.application.use_cases import RequestActionResult


class RequestActionResponse(BaseModel):
    status: str
    decision: str
    reason: str
    approval_request_id: str | None = None

    @classmethod
    def from_result(cls, result: RequestActionResult) -> "RequestActionResponse":
        return cls(
            status=result.status.value,
            decision=result.evaluation.decision.value,
            reason=result.evaluation.reason,
            approval_request_id=(
                result.approval_request.request_id
                if result.approval_request is not None
                else None
            ),
        )
```

Co tu jest ważne:

- API response nie musi zwracać całego `ApprovalRequest`.
- Nie pokazujemy przypadkowo pól wewnętrznych.
- `from_result()` jest jawne i łatwe do debugowania.
- Adapter decyduje, jaki kształt JSON zobaczy klient.

### Endpoint z Pydantic i use case

```python
from fastapi import APIRouter, Depends

from secure_agentic_ai.adapters.api.schemas import (
    RequestActionPayload,
    RequestActionResponse,
)
from secure_agentic_ai.application.use_cases import RequestActionUseCase

router = APIRouter()


@router.post("/actions", response_model=RequestActionResponse)
async def request_action(
    payload: RequestActionPayload,
    use_case: RequestActionUseCase = Depends(get_request_action_use_case),
) -> RequestActionResponse:
    command = payload.to_command()
    result = use_case.execute(command)
    return RequestActionResponse.from_result(result)
```

W tej wersji endpoint jest `async`, ale sam use case jest synchroniczny.

To jest OK na tym etapie, bo use case nie robi I/O. Później, gdy pojawią się async repository adapters, podejmiemy decyzję, czy use case też ma być async.

### Walidacja Pydantic w praktyce

Jeśli klient wyśle:

```json
{
  "request_id": "",
  "actor_id": "agent-001",
  "actor_type": "agent",
  "actor_display_name": "Developer Agent",
  "action_type": "file.write",
  "risk_level": "high",
  "action_description": "Write generated source file"
}
```

FastAPI/Pydantic zwróci błąd `422`, bo `request_id` ma `min_length=1`.

Jeśli klient wyśle:

```json
{
  "actor_type": "robot"
}
```

Pydantic odrzuci request, bo `"robot"` nie należy do `ActorType`.

### `model_dump()` i `model_validate()`

W Pydantic v2 podstawowe metody to:

```python
payload.model_dump()
payload.model_dump_json()
RequestActionPayload.model_validate(data)
RequestActionPayload.model_validate_json(raw_json)
```

Nie używamy już mentalnie stylu Pydantic v1 typu `.dict()` jako podstawowego API. W v2 myślimy:

```text
model_dump      -> Python dict
model_dump_json -> JSON string
model_validate  -> dict/object into model
```

### Mentalny model Pydantic

Pydantic nie jest tylko "ładniejszą klasą z polami". To runtime parser danych.

Najprostszy model:

```text
nieufne dane z zewnątrz
        |
        v
Pydantic BaseModel
        |
        v
sprawdzone, ustrukturyzowane dane w Pythonie
```

W naszym projekcie Pydantic ma pilnować granicy systemu:

```text
HTTP / JSON / query params / env vars
        |
        v
Pydantic schema
        |
        v
application command albo response DTO
```

To jest ważne, bo dane z HTTP są zawsze podejrzane. Nawet jeśli request wysyłamy sami z testów, API powinno zachowywać się tak, jakby klient mógł wysłać:

- pusty string,
- zły enum,
- brak pola,
- dodatkowe pole,
- liczbę jako string,
- listę zamiast stringa,
- payload większy niż zakładaliśmy.

Pydantic daje nam pierwszą linię obrony przed chaosem wejścia. Nie zastępuje security policy, ale usuwa bałagan z adaptera.

### `BaseModel` jako DTO granicy

Minimalny model Pydantic wygląda tak:

```python
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
```

Użycie:

```python
response = HealthResponse(status="ok")

assert response.status == "ok"
assert response.model_dump() == {"status": "ok"}
assert response.model_dump_json() == '{"status":"ok"}'
```

Co jest tu istotne:

- pola są deklarowane przez type hints,
- Pydantic waliduje wartości w runtime,
- model można łatwo zamienić na `dict` albo JSON,
- FastAPI potrafi z tego automatycznie wygenerować OpenAPI.

### Typy, ograniczenia i `Field`

Same type hints często nie wystarczą. Dla API potrzebujemy też prostych ograniczeń.

```python
from pydantic import BaseModel, Field


class RequestActionPayload(BaseModel):
    request_id: str = Field(min_length=1, max_length=120)
    actor_id: str = Field(min_length=1, max_length=120)
    action_description: str = Field(min_length=1, max_length=500)
```

`Field(...)` opisuje kontrakt danych:

- `min_length=1` blokuje pusty string,
- `max_length=120` ogranicza rozmiar pola,
- `description="..."` może opisać pole w OpenAPI,
- `examples=[...]` może dać przykłady w dokumentacji API.

Przykład z opisami:

```python
class RequestActionPayload(BaseModel):
    request_id: str = Field(
        min_length=1,
        max_length=120,
        description="Client-generated request identifier.",
        examples=["req-001"],
    )
```

W publicznym API takie ograniczenia są sygnałem jakości: pokazują, że nie traktujemy JSON-a jak luźnego worka.

### Enums w Pydantic

Nasze enumy domenowe mogą być używane w schemach API:

```python
from secure_agentic_ai.domain.actors import ActorType
from secure_agentic_ai.domain.policies import ActionType, RiskLevel


class RequestActionPayload(BaseModel):
    actor_type: ActorType
    action_type: ActionType
    risk_level: RiskLevel
```

Jeśli enum dziedziczy po `StrEnum`, JSON będzie czytelny:

```json
{
  "actor_type": "agent",
  "action_type": "file.write",
  "risk_level": "high"
}
```

To daje trzy korzyści:

- FastAPI pokaże dozwolone wartości w OpenAPI,
- Pydantic odrzuci nieznane wartości,
- application layer dostanie już poprawny typ, nie przypadkowy string.

### Modele zagnieżdżone

Możemy trzymać jeden płaski request payload albo podzielić go na mniejsze modele.

Płaski model jest prostszy na start:

```python
class RequestActionPayload(BaseModel):
    request_id: str
    actor_id: str
    actor_type: ActorType
    actor_display_name: str
    action_type: ActionType
    risk_level: RiskLevel
    action_description: str
```

Model zagnieżdżony jest czytelniejszy, gdy API zaczyna rosnąć:

```python
class ActorPayload(BaseModel):
    actor_id: str = Field(min_length=1)
    actor_type: ActorType
    display_name: str = Field(min_length=1)


class ActionPayload(BaseModel):
    action_type: ActionType
    risk_level: RiskLevel
    description: str = Field(min_length=1)


class RequestActionPayload(BaseModel):
    request_id: str = Field(min_length=1)
    actor: ActorPayload
    action: ActionPayload
```

Dla Fazy 4 oba warianty są akceptowalne. Ja preferuję wersję płaską, jeśli celem jest nauka przepływu `Payload -> Command`, a wersję zagnieżdżoną, jeśli chcemy od razu ćwiczyć projektowanie kontraktu API.

### Jawne mapowanie do command

Najważniejsze: Pydantic schema nie powinna "przeciekać" do use case'a.

Nie chcemy tego:

```python
# ZLE
result = use_case.execute(payload)
```

Chcemy to:

```python
# DOBRZE
command = payload.to_command()
result = use_case.execute(command)
```

Dlaczego?

```text
API schema:
  mówi językiem HTTP/JSON

Application command:
  mówi językiem przypadku użycia

Domain objects:
  mówią językiem reguł biznesowych
```

To mapowanie może wydawać się "nadmiarowe", ale jest dokładnie tym miejscem, które chroni core przed frameworkiem.

### Walidatory Pydantic

Pydantic ma walidatory pól i modeli. W Fazie 4 używamy ich ostrożnie.

Przykład walidatora pola:

```python
from pydantic import BaseModel, field_validator


class RequestActionPayload(BaseModel):
    request_id: str

    @field_validator("request_id")
    @classmethod
    def request_id_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("request_id must not be blank")
        return stripped
```

Przykład walidatora całego modelu:

```python
from typing import Self

from pydantic import BaseModel, model_validator


class RequestActionPayload(BaseModel):
    actor_id: str
    actor_display_name: str

    @model_validator(mode="after")
    def actor_display_name_must_not_duplicate_id(self) -> Self:
        if self.actor_display_name == self.actor_id:
            raise ValueError("actor_display_name should be human-readable")
        return self
```

Ale tu jest ważna granica:

```text
Pydantic validator:
  format, obecność, proste zależności między polami

Domain/application:
  reguły policy, approval, audit, security decision
```

Nie wkładamy do walidatora pytania "czy agent może wykonać akcję". To robi `evaluate_policy()` i use case.

### Strict mode i konwersje

Pydantic domyślnie bywa pomocny: próbuje konwertować typy.

```python
from pydantic import BaseModel


class QueryPayload(BaseModel):
    limit: int


payload = QueryPayload.model_validate({"limit": "10"})
assert payload.limit == 10
```

To bywa wygodne dla query params, ale przy danych security-sensitive może być zbyt liberalne.

Można użyć typów strict:

```python
from pydantic import BaseModel, StrictInt, StrictStr


class StrictPayload(BaseModel):
    request_id: StrictStr
    retry_count: StrictInt
```

Wtedy `"10"` nie przejdzie jako `int`.

Robocza zasada dla naszego projektu:

```text
API ergonomiczne pola:
  umiarkowana konwersja jest OK

security-sensitive pola:
  preferuj jawność, enumy, ograniczenia i stricter validation
```

### `extra`: co z dodatkowymi polami?

Domyślnie warto świadomie zdecydować, co robimy z polami, których nie znamy.

Przykład:

```json
{
  "request_id": "req-001",
  "actor_id": "agent-001",
  "unexpected_admin_override": true
}
```

Dla API security-first sensowne jest odrzucanie nieznanych pól:

```python
from pydantic import BaseModel, ConfigDict


class RequestActionPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
```

Opcje:

```text
extra="ignore"  -> ignoruj nieznane pola
extra="forbid"  -> odrzuć request z nieznanymi polami
extra="allow"   -> dopuść nieznane pola
```

Dla tego projektu preferencja: `extra="forbid"` na publicznych request schemach. To pasuje do zasady "deny by default".

### Aliasy pól: Python snake_case vs JSON

W Pythonie używamy `snake_case`.

W JSON API często też możemy używać `snake_case`, zwłaszcza w portfolio technicznym. Jeśli jednak chcielibyśmy `camelCase`, Pydantic to obsłuży.

```python
from pydantic import BaseModel, Field


class RequestActionPayload(BaseModel):
    request_id: str = Field(alias="requestId")
```

Wtedy JSON:

```json
{
  "requestId": "req-001"
}
```

Na tym etapie nie komplikowałbym API aliasami. `snake_case` jest prostszy, spójny z Pythonem i wystarczający.

### Response model jako filtr bezpieczeństwa

`response_model` w FastAPI nie jest tylko dokumentacją. To także filtr odpowiedzi.

```python
@router.post("/actions", response_model=RequestActionResponse)
async def request_action(...) -> RequestActionResponse:
    ...
```

Dlaczego to ważne?

```text
Use case result może zawierać więcej niż chcemy pokazać klientowi.
Response schema określa publiczny kontrakt odpowiedzi.
```

W projekcie security-first to ma znaczenie. Nie chcemy przypadkiem zwrócić:

- wewnętrznego obiektu domenowego,
- pełnego audit eventu,
- danych debugowych,
- ścieżek lokalnych,
- informacji o sekretach.

Dlatego `RequestActionResponse.from_result()` powinien być jawny i oszczędny.

### Testowanie Pydantic i API

W Fazie 4 testujemy dwa poziomy:

```text
schema tests:
  czy Pydantic przyjmuje/odrzuca payload

API tests:
  czy endpoint mapuje request do use case'a i zwraca poprawny HTTP response
```

Przykład testu samej schemy:

```python
import pytest
from pydantic import ValidationError

from secure_agentic_ai.adapters.api.schemas import RequestActionPayload


def test_request_action_payload_rejects_empty_request_id() -> None:
    with pytest.raises(ValidationError):
        RequestActionPayload.model_validate(
            {
                "request_id": "",
                "actor_id": "agent-001",
                "actor_type": "agent",
                "actor_display_name": "Agent",
                "action_type": "context.read",
                "risk_level": "low",
                "action_description": "Read context",
            }
        )
```

Przykład testu API:

```python
from fastapi.testclient import TestClient

from secure_agentic_ai.adapters.api.app import create_app


def test_request_action_endpoint_allows_low_risk_human_action() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/actions",
        json={
            "request_id": "req-001",
            "actor_id": "human-001",
            "actor_type": "human",
            "actor_display_name": "Human Operator",
            "action_type": "context.read",
            "risk_level": "low",
            "action_description": "Read context",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "allowed"
```

Debugowanie takiego testu będzie bardzo dobre edukacyjnie, bo można przejść breakpointami przez:

```text
JSON request
-> Pydantic payload
-> to_command()
-> use_case.execute()
-> evaluate_policy()
-> RequestActionResponse.from_result()
-> JSON response
```

To jest dokładnie przepływ, który chcemy zrozumieć w tej fazie.

### Pydantic a OpenAPI

FastAPI używa Pydantic modeli do wygenerowania dokumentacji API.

To znaczy, że dobrze opisany model:

```python
class RequestActionPayload(BaseModel):
    request_id: str = Field(
        min_length=1,
        description="Client-generated request identifier.",
        examples=["req-001"],
    )
```

przełoży się na czytelniejsze:

- `/docs`,
- `/openapi.json`,
- dokumentację requestów,
- dokumentację response'ów.

Dla rekrutera to jest dobry sygnał: API nie jest przypadkowe, tylko ma kontrakt.

### Czego unikać z Pydantic

Nie rób z Pydantic modelu domenowego:

```python
# ZLE na tym etapie
class ApprovalRequest(BaseModel):
    ...
```

Dlaczego?

- domena zaczęłaby zależeć od Pydantic,
- reguły biznesowe mieszałyby się z walidacją wejścia HTTP,
- trudniej byłoby później użyć domeny z CLI, LangGraph albo testów bez API,
- Pydantic jest świetny na granicach systemu, ale nie musi być w środku domeny.

Nie wkładaj całego use case'a do walidatora:

```python
# ZLE
@model_validator(mode="after")
def check_policy(self) -> "RequestActionPayload":
    ...
```

Walidator może sprawdzić format danych, ale policy to domena/application.

## Czego nie robimy w tej fazie

- PostgreSQL,
- SQLAlchemy,
- LangGraph,
- RAG,
- realne LLM calls,
- Bitwarden,
- kosztów i observability.

## Checklist

- [ ] 1. Zrobić krótki spike FastAPI poza publicznym commitem, jeśli async/Pydantic nadal nie są wygodne.
- [ ] 2. Dodać `adapters/api/app.py`.
- [ ] 3. Dodać endpoint `GET /health`.
- [ ] 4. Dodać Pydantic schemas dla request action.
- [ ] 5. Dodać route, który buduje `RequestActionCommand`.
- [ ] 6. Podpiąć `RequestActionUseCase` przez dependency.
- [ ] 7. Dodać in-memory fake adapter dla repository/audit.
- [ ] 8. Przetestować ścieżkę `ALLOW`.
- [ ] 9. Przetestować ścieżkę `DENY`.
- [ ] 10. Przetestować ścieżkę `REQUIRE_APPROVAL`.
- [ ] 11. Sprawdzić OpenAPI.
- [ ] 12. Uruchomić quality gate.

## Referencje do PHP

### FastAPI route vs Symfony/Laravel controller

Route nie może stać się miejscem na logikę biznesową.

```text
PHP:
Request -> Controller -> Service -> Response

Python:
HTTP request -> FastAPI route -> Command -> UseCase -> Result -> Response schema
```

```php
// PHP — controller jest cienkim adapterem HTTP
final class RequestActionController
{
    public function __invoke(Request $request): JsonResponse
    {
        $command = new RequestActionCommand(
            actorId: $request->get('actor_id'),
            actionType: $request->get('action_type'),
        );

        return new JsonResponse($this->useCase->execute($command));
    }
}
```

```python
# Python — route też ma być cienkim adapterem HTTP
@router.post("/actions")
async def request_action(
    payload: RequestActionPayload,
    use_case: RequestActionUseCase = Depends(get_request_action_use_case),
) -> RequestActionResponse:
    command = payload.to_command()
    result = use_case.execute(command)
    return RequestActionResponse.from_result(result)
```

**Implikacje dla Python:**

- FastAPI route tłumaczy HTTP, nie zawiera reguł policy.
- Pydantic payload nie jest modelem domenowym.
- Use case powinien dać się przetestować bez serwera HTTP.

### Pydantic vs Symfony Validator / FormRequest / DTO

Pydantic jest najbliżej połączenia DTO, walidatora i serializera.

```text
PHP:
Request data -> DTO/FormRequest -> Validator -> Service command

Python/FastAPI:
JSON body -> Pydantic BaseModel -> Command -> UseCase
```

```php
// PHP — DTO + walidacja przez atrybuty/Symfony Validator
final class RequestActionDto
{
    public function __construct(
        #[Assert\NotBlank]
        public string $requestId,

        #[Assert\Choice(['human', 'agent'])]
        public string $actorType,
    ) {}
}
```

```python
# Python — Pydantic łączy DTO i walidację
class RequestActionPayload(BaseModel):
    request_id: str = Field(min_length=1)
    actor_type: ActorType
```

**Implikacje dla Python:**

- Type hints w Pydantic są aktywnie używane do walidacji runtime.
- Błąd walidacji daje automatyczny response `422` w FastAPI.
- To nadal nie jest model domenowy.
- Mapowanie `Payload -> Command` powinno być jawne.

### Pydantic coercion vs ścisłe typy

Pydantic potrafi konwertować dane wejściowe, co jest wygodne, ale bywa zdradliwe.

```text
PHP:
Walidacja często jawnie mówi, czy string "123" jest akceptowany jako int.

Pydantic:
Domyślnie może próbować skonwertować "123" na int.
```

```php
// PHP — często sam decydujesz, czy cast jest OK
$limit = (int) $request->query->get('limit', 10);
```

```python
# Python — Pydantic może sparsować string do int
class ListQuery(BaseModel):
    limit: int = Field(default=10, ge=1, le=100)

query = ListQuery.model_validate({"limit": "20"})
assert query.limit == 20
```

**Implikacje dla Python:**

- W API to często wygodne.
- Przy security-sensitive polach warto rozważyć typy stricter.
- Nie zakładaj, że Pydantic zawsze działa jak statyczny type checker.
- `mypy` sprawdza kod przed runtime, Pydantic waliduje dane w runtime.

### Long-running process vs PHP-FPM

To jest największa pułapka dla PHP-developera.

```text
PHP-FPM:
Każdy request startuje ze świeżą pamięcią.

FastAPI/ASGI:
Proces żyje długo. Zasoby globalne mogą istnieć godzinami.
```

```php
// PHP — per request często jest normalne
$client = new HttpClient();
$response = $client->get($url);
```

```python
# Python — ciężkie klienty/pule lepiej tworzyć raz
app = FastAPI()

@app.on_event("startup")
async def startup() -> None:
    app.state.http_client = AsyncClient()
```

**Implikacje dla Python:**

- Nie twórz connection poola per request.
- Uważaj na globalny mutowalny stan.
- Startup/shutdown aplikacji są ważną częścią architektury.

## Oczekiwany rezultat fazy

Po Fazie 4 mamy minimalne API, ale core nadal jest niezależny od FastAPI. Rekruter może zobaczyć, że framework jest adapterem, nie centrum systemu.
