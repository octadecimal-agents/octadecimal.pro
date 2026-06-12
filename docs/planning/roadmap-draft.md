<link rel="stylesheet" href="../styles/main.css">

# Wstępna roadmapa projektu

[← Indeks planowania](README.md)

Status: prywatny szkic roboczy, do dalszego pogłębiania

Ten dokument opisuje, jak rozegrać projekt jako portfolio AI Engineera i jednocześnie ścieżkę nauki code-first Python. To nie jest jeszcze publiczny `ROADMAP.md`. Najpierw potrzebujemy prywatnie ustalić logikę faz, zanim cokolwiek pokażemy w repo.

## Zasada nadrzędna

Każda faza ma mieć trzy efekty:

- realny przyrost działającego systemu,
- przyrost wiedzy właściciela projektu,
- czytelny sygnał dla rekrutera.

Nie budujemy "dużo". Budujemy tak, żeby każdy commit dało się obronić technicznie.

## Obecny stan

Publiczne repo ma już:

- `README.md`,
- `LICENSE`,
- `CONTRIBUTING.md`,
- `SECURITY.md`,
- `.gitignore`.

Niecommitowane są obecnie:

- `docs/`,
- `install/`.

Te artefakty pochodzą z poprzedniego kierunku myślenia o macOS local runtime. Nie należy ich commitować automatycznie. Trzeba zdecydować, czy:

- przenieść je do `.dev/research/`,
- skrócić do małego optional appendix,
- całkiem odłożyć,
- albo wykorzystać później jako security case study.

Domyślna rekomendacja: **nie commitować ich teraz**.

## Narracja docelowa

Publiczna narracja projektu:

> Secure Agentic AI Platform demonstrates how to build governed, observable and evaluation-driven AI workflows using modern Python, LangGraph, RAG, HITL approvals and audit-ready architecture.

Prywatna narracja nauki:

> Przechodzę z wieloletniego doświadczenia klasycznego web/backend engineeringu do AI Engineeringu przez świadome, testowane, code-first budowanie platformy agentic AI.

## Decyzje po korekcie roadmapy

Po przeglądzie dodatkowych materiałów i propozycji poprawek przyjmujemy następujące decyzje:

- Faza 3 nie jest FastAPI. Faza 3 to `application layer`, use case'y, porty i testy bez frameworków.
- FastAPI wchodzi dopiero po application layer jako cienki adapter/API boundary.
- Części zewnętrzne systemu są **async-first**: FastAPI, database adapters, LLM calls, LangGraph execution, Qdrant, observability.
- `domain` pozostaje zwykłym, synchronicznym, czystym Pythonem.
- MCP dodajemy do roadmapy, ale nie jako fundament. Najpierw musi istnieć działający core.
- Observability musi obejmować nie tylko traces i evals, ale też koszty: token usage, model cost estimate, latency, cache hit ratio.
- Agent memory traktujemy jawnie: checkpointing jako pamięć krótkoterminowa, RAG/vector store jako pamięć długoterminowa.
- UI/operator console jest opcjonalnym demo, nie głównym sygnałem AI Engineer.
- Nauka idzie przez portfolio, ale przed nowym mental modelem robimy krótki spike.

## Strategia nauki

Nie robimy osobnego, długiego kursu Pythona przed portfolio. Główny tor to projekt.

Robimy za to krótkie spike'i przed obszarami, które wymagają nowego modelu myślenia:

```text
Application layer:
  bez spike'a, czysty Python i architektura

FastAPI async:
  1 dzień spike: async endpoint, Pydantic, TestClient/httpx

SQLAlchemy async:
  1 dzień spike: async engine, session, transaction, rollback test

LangGraph:
  2 dni spike: graph, conditional edge, interrupt/resume, checkpoint

RAG:
  1-2 dni spike: chunking, embedding, retrieval, reranking mini-case

MCP:
  1 dzień spike: minimal MCP server/client, tool exposure, safety boundary
```

Materiały w `.dev/questions` są mapą powtórkową do rozmów, nie linearnym kursem. Korzystamy z nich wtedy, gdy dana faza dotyka konkretnego tematu.

## Faza 0: Strategic Baseline

Cel: ustalić ramy projektu i zatrzymać dryf w stronę przypadkowych eksperymentów.

### Zakres

- prywatny plan projektu w `.dev`,
- decyzja, co zrobić z obecnym `docs/` i `install/`,
- publiczne minimum: README, CONTRIBUTING, SECURITY, `.gitignore`,
- publiczna roadmapa dopiero po ustaleniu faz.

### Artefakty prywatne

- `.dev/SESSION_CONTEXT.md`,
- `.dev/explanations/idea.md`,
- `.dev/planning/roadmap-draft.md`,
- `.dev/docs/` jako polskie tłumaczenia publicznych dokumentów,
- `.dev/technologies/` jako baza wiedzy.

### Artefakty publiczne

Na tym etapie prawdopodobnie nic nowego, chyba że zdecydujemy się dodać krótki `ROADMAP.md`.

### Umiejętności demonstrowane rekruterowi

- świadome prowadzenie projektu,
- security-first governance,
- brak chaotycznego generowania kodu,
- dobra higiena repo.

### Kryterium ukończenia

- mamy zaakceptowany prywatny plan faz,
- wiemy, jaki będzie pierwszy techniczny vertical slice,
- niecommitowane artefakty zostały sklasyfikowane.

### Referencje do PHP

```text
To etap podobny do decyzji architektonicznych przed dużym projektem Symfony/Laravel:
zanim powstaną kontrolery i encje, ustalamy granice modułów, konwencje i historię,
którą projekt ma opowiadać.
```

## Faza 1: Python Platform Foundation

Cel: postawić minimalny, profesjonalny fundament Pythona.

### Zakres

- `pyproject.toml`,
- `uv` jako package/environment manager,
- struktura pakietu,
- `ruff`,
- `mypy`,
- `pytest`,
- minimalny test,
- GitHub Actions dla jakości kodu,
- README update z komendami developerskimi.

### Proponowana struktura

```text
src/secure_agentic_ai/
├── __init__.py
├── domain/
├── application/
├── adapters/
└── infrastructure/

tests/
├── unit/
├── integration/
└── evals/
```

### Publiczne commity

1. `chore(python): initialize project tooling`
2. `test: add initial test structure`
3. `chore(ci): add Python quality workflow`

### Wiedza do opanowania

- `pyproject.toml`,
- `uv`,
- struktura pakietu Python,
- importy w Pythonie,
- pytest basics,
- ruff,
- mypy basics.

### Sygnał dla rekrutera

Projekt nie jest tylko deklaracją o AI. Ma profesjonalny fundament backendowy.

### Kryterium ukończenia

- `uv run pytest` działa,
- `uv run ruff check .` działa,
- `uv run mypy .` działa,
- GitHub Actions przechodzi.

### Referencje do PHP

```text
pyproject.toml pełni rolę zbliżoną do composer.json, ale szerzej:
opisuje projekt, dependencies, build backend i konfiguracje narzędzi.

uv jest odpowiednikiem połączenia Composer + manager środowiska.

ruff/mypy/pytest to odpowiedniki praktyk typu PHP-CS-Fixer/PHPStan/PHPUnit,
ale w Pythonie od początku ustawiamy je jako quality gate.
```

## Faza 2: Domain Model For Governance

Cel: zbudować czysty model domenowy dla approval, policy i audit.

### Zakres

- `Actor`,
- `Action`,
- `Capability`,
- `ApprovalRequest`,
- `ApprovalDecision`,
- `AuditEvent`,
- statusy workflow,
- reguły przejść stanów,
- testy unit dla allowed/denied transitions.

### Ważna decyzja

Na tym etapie nie używać jeszcze FastAPI, LangGraph ani bazy danych w domenie. Najpierw domena ma działać jako czysty Python.

### Publiczne commity

1. `feat(domain): add approval request model`
2. `feat(domain): add policy decision model`
3. `test(domain): cover approval state transitions`
4. `feat(domain): add audit event model`

### Wiedza do opanowania

- dataclasses vs Pydantic vs plain classes,
- value objects,
- enumy,
- wyjątki domenowe,
- testowanie reguł biznesowych.

### Sygnał dla rekrutera

Kandydat rozumie, że agentic AI potrzebuje jawnego modelu governance, a nie tylko promptów.

### Kryterium ukończenia

- domena ma testy,
- denied paths są testowane,
- model można wyjaśnić bez frameworków.

### Referencje do PHP

```text
Domain w tej fazie jest najbliższy czystym modelom biznesowym w DDD,
nie encjom Doctrine/Eloquent.

To nie jest jeszcze warstwa bazy danych. To język biznesu:
Actor, Action, PolicyDecision, ApprovalRequest.

W PHP łatwo wejść w model "Entity = tabela". Tutaj celowo tego unikamy.
```

## Faza 3: Application Layer And Governance Use Cases

Cel: opakować domenę w przypadki użycia bez wchodzenia jeszcze w FastAPI, bazę danych, LangGraph ani frameworki.

### Zakres

- command objects,
- use case `RequestActionUseCase`,
- result objects,
- porty przez `Protocol`,
- fake repository w testach,
- fake audit writer w testach,
- testy ścieżek `ALLOW`, `DENY`, `REQUIRE_APPROVAL`.

### Publiczne commity

1. `feat(application): add action request use case`
2. `test(application): cover policy decision paths`
3. `feat(application): add approval repository and audit ports`

### Wiedza do opanowania

- dataclasses jako commands/results,
- `Protocol`,
- dependency inversion,
- fake implementations w testach,
- use case jako orchestration, nie reguła domenowa.

### Sygnał dla rekrutera

Kandydat umie projektować kod od środka systemu, a nie zaczynać od frameworka.

### Kryterium ukończenia

- use case przechodzi testy,
- application nie zna FastAPI ani SQLAlchemy,
- domain nadal nie importuje application,
- porty są opisane przez `Protocol`.

### Referencje do PHP

```text
Application use case jest podobny do Service/ApplicationService w Symfony,
ale powinien być bardziej jawny i lepiej typowany.

Port przez Protocol jest podobny do zależności od interfejsu w PHP:
use case nie wie, czy repozytorium jest w pamięci, PostgreSQL czy pliku.

To różni się od typowego Laravelowego podejścia, gdzie controller często szybko
zaczyna znać request, model, bazę i reguły naraz.
```

## Faza 4: FastAPI Async Application Boundary

Cel: wystawić pierwszy API boundary dla approval workflow jako cienki adapter nad application layer.

### Zakres

- FastAPI app,
- health endpoint,
- endpoint request action,
- endpoint approve/reject,
- Pydantic v2 request/response schemas,
- in-memory adapter repository,
- testy API przez `httpx` albo `TestClient`,
- decyzja async-first dla API.

### Publiczne commity

1. `feat(api): add FastAPI application shell`
2. `feat(api): expose approval request endpoints`
3. `test(api): cover approval API flow`

### Wiedza do opanowania

- FastAPI routing,
- async endpointy,
- Pydantic v2,
- dependency injection w FastAPI,
- `httpx`/TestClient,
- rozdział schema vs domain model.

### Sygnał dla rekrutera

Projekt zaczyna być używalnym backendem, ale framework pozostaje cienką warstwą wejścia.

### Kryterium ukończenia

- API przechodzi testy,
- OpenAPI generuje sensowne schema,
- domena nadal nie importuje FastAPI,
- application nadal nie zależy od FastAPI.

### Referencje do PHP

```text
FastAPI route jest odpowiednikiem kontrolera Symfony/Laravel,
ale nie powinien zawierać logiki biznesowej.

Pydantic schema jest bliższe DTO/FormRequest/Validator niż encji domenowej.

Największa różnica względem PHP-FPM: aplikacja Pythonowa jest long-running.
Nie tworzymy kosztownych zasobów per request, jeśli powinny istnieć jako singleton/pool.
```

## Faza 5: Async Persistence And Audit Trail

Cel: przenieść stan z pamięci do PostgreSQL i dodać realny audit trail.

### Zakres

- Docker Compose dla PostgreSQL,
- SQLAlchemy 2.0 async,
- Alembic,
- tabele approval requests,
- tabele audit events,
- async repository adapter,
- integration tests.

### Publiczne commity

1. `chore(docker): add PostgreSQL service`
2. `feat(db): add approval persistence`
3. `feat(audit): persist audit events`
4. `test(integration): cover approval persistence`

### Wiedza do opanowania

- SQLAlchemy 2.0,
- async engine/session,
- Alembic migrations,
- transakcje,
- repozytorium jako adapter.

### Sygnał dla rekrutera

Kandydat umie przełożyć model domenowy na trwały, testowany backend.

### Kryterium ukończenia

- migracje działają od zera,
- API używa PostgreSQL,
- testy integracyjne przechodzą,
- audit event powstaje dla każdej decyzji.

### Referencje do PHP

```text
SQLAlchemy ORM nie jest Doctrine jeden do jednego.

W PHP-FPM każde żądanie zwykle żyje krótko, a połączenie do bazy często jest
zarządzane przez runtime/request lifecycle. W Python FastAPI proces żyje długo,
więc connection pool i session lifecycle trzeba zaprojektować świadomie.

Repository adapter pełni rolę podobną do implementacji interfejsu repozytorium,
ale use case nie powinien znać SQLAlchemy session.
```

## Faza 6: LangGraph HITL Workflow And Agent Memory

Cel: zbudować pierwszy agentic workflow z przerwaniem na approval.

### Zakres

- minimalny LangGraph state,
- node proponujący action,
- policy check node,
- HITL interrupt/wait state,
- resume po decyzji,
- executor stub,
- audit eventy dla kroków,
- checkpointing jako short-term memory,
- decyzja, co jest state, a co trwałym audit/persistence.

### Publiczne commity

1. `feat(workflow): add LangGraph approval flow`
2. `test(workflow): cover HITL pause and resume`
3. `feat(audit): trace workflow decisions`

### Wiedza do opanowania

- LangGraph state,
- nodes,
- edges,
- conditional routing,
- interrupts/checkpointing,
- short-term memory,
- testowanie workflow.

### Sygnał dla rekrutera

To pierwszy punkt, gdzie projekt staje się realnie "agentic", ale nadal z governance.

### Kryterium ukończenia

- workflow zatrzymuje się na approval,
- można go wznowić,
- brak approval blokuje wykonanie,
- testy potwierdzają flow,
- checkpointing jest wyjaśniony jako pamięć krótkoterminowa workflow.

### Referencje do PHP

```text
LangGraph nie jest kolejką jobów ani kontrolerem.
Najbliższe skojarzenie z PHP to state machine/workflow component,
ale z węzłami, stanem i możliwością przerwania/wznowienia.

Checkpointing można porównać do zapisu stanu procesu długiego trwania,
czego klasyczne aplikacje PHP request-response zwykle unikają albo wypychają do kolejki.
```

## Faza 7: RAG Foundation

Cel: dodać kontrolowany subsystem wiedzy.

### Zakres

- dokumenty testowe,
- ingestion pipeline,
- chunking,
- embeddings interface,
- Qdrant albo pgvector jako pierwszy backend,
- retriever port,
- podstawowy RAG query endpoint/use case,
- testy retrieval.

### Publiczne commity

1. `feat(rag): add document ingestion model`
2. `feat(rag): add retriever port`
3. `feat(rag): add vector backend adapter`
4. `test(rag): cover retrieval behavior`

### Wiedza do opanowania

- chunking,
- embeddings,
- metadata,
- vector search,
- retrieval quality,
- Qdrant vs pgvector tradeoffs.

### Sygnał dla rekrutera

Kandydat rozumie RAG jako pipeline z kontrolą jakości, nie "wrzuć PDF do wektorów".

### Kryterium ukończenia

- ingestion jest powtarzalny,
- retrieval zwraca oczekiwany kontekst,
- backend jest za portem,
- dane testowe nie są prywatne.

### Referencje do PHP

```text
RAG nie jest "wyszukiwarką LIKE po bazie".

Najbliższe porównanie z klasycznego backendu:
ingestion pipeline przypomina indeksowanie do Elasticsearch,
a retrieval przypomina wyszukiwanie kontekstu przed wykonaniem logiki.

Różnica: wyniki retrieval trafiają później do promptu, więc jakość i bezpieczeństwo
kontekstu są częścią logiki aplikacji.
```

## Faza 8: AI Security And Prompt Injection

Cel: dodać jawne kontrole bezpieczeństwa LLM.

### Zakres

- prompt injection patterns,
- input classifier/rules,
- retrieved-context safety checks,
- policy dla tool use,
- testy negative cases,
- pierwsze security evals.

### Publiczne commity

1. `security(prompt): add injection detection rules`
2. `test(security): cover malicious retrieved context`
3. `feat(policy): require approval for risky tool actions`

### Wiedza do opanowania

- OWASP LLM risks,
- direct vs indirect prompt injection,
- tool abuse,
- data exfiltration,
- guardrails vs policy engine.

### Sygnał dla rekrutera

Projekt nie tylko używa LLM, ale rozumie specyficzne ryzyka LLM.

### Kryterium ukończenia

- istnieją testy na prompt injection,
- unsafe tool call nie przechodzi bez approval,
- system nie wkłada sekretów do prompt context.

### Referencje do PHP

```text
Prompt injection jest podobne do SQL injection tylko na poziomie instrukcji dla modelu,
ale nie działa przez parser SQL, tylko przez konflikt instrukcji i zaufania do danych.

Tak jak w PHP nie wolno sklejać SQL z inputem użytkownika,
tak w AI nie wolno bezkrytycznie traktować retrieved/user content jako instrukcji systemowej.
```

## Faza 9: Observability, Evals And Cost Monitoring

Cel: uczynić zachowanie systemu mierzalnym.

### Zakres

- Langfuse integration,
- OpenTelemetry traces,
- trace IDs w audit events,
- basic eval dataset,
- eval runner,
- raport evals w CI albo lokalnie,
- token usage,
- szacowanie kosztu per request,
- latency per provider/model,
- cache hit ratio.

### Publiczne commity

1. `feat(observability): add tracing baseline`
2. `feat(evals): add approval safety evals`
3. `feat(evals): add RAG quality evals`

### Wiedza do opanowania

- traces,
- spans,
- Langfuse observations,
- eval datasets,
- LLM-as-judge ograniczenia,
- regression evals,
- metryki kosztów i limitów.

### Sygnał dla rekrutera

Kandydat rozumie production AI: jakość i koszt trzeba mierzyć, nie zgadywać.

### Kryterium ukończenia

- workflow emituje trace,
- evals można uruchomić lokalnie,
- wynik evals jest czytelny,
- wrażliwe dane nie trafiają do traces,
- koszt i liczba tokenów są widoczne w metrykach lub audit/debug output.

### Referencje do PHP

```text
To odpowiednik połączenia logów aplikacyjnych, APM, metryk biznesowych i testów regresji.

Różnica względem typowego backendu:
w systemie LLM koszt pojedynczego requestu nie jest stały. Zależy od liczby tokenów,
modelu, retry, RAG context i długości odpowiedzi.
```

## Faza 10: MCP Integration And External Tool Context

Cel: dodać kontrolowany sposób wystawiania narzędzi/kontekstu dla modeli i agentów przez MCP.

### Zakres

- minimalny MCP server albo client spike,
- port/adapter dla tool context,
- jawne granice dostępnych operacji,
- testy denied/allowed tool exposure,
- dokumentacja, co jest narzędziem, a co akcją domenową.

### Publiczne commity

1. `feat(mcp): add minimal tool context adapter`
2. `test(mcp): cover allowed and denied tool exposure`
3. `docs(mcp): describe tool boundary`

### Wiedza do opanowania

- MCP server/client model,
- tool exposure,
- granice zaufania,
- różnica między action, tool i adapterem,
- bezpieczeństwo integracji agentów z narzędziami.

### Sygnał dla rekrutera

Kandydat rozumie współczesny ekosystem agentów i potrafi kontrolować dostęp modeli do narzędzi.

### Kryterium ukończenia

- istnieje minimalna, testowalna integracja MCP,
- narzędzia nie obchodzą policy,
- MCP jest adapterem, nie logiką domenową.

### Referencje do PHP

```text
MCP można porównać do standaryzowanego API/plugin systemu dla agentów.
W PHP analogią może być wystawienie zestawu endpointów/komend dla zewnętrznego klienta,
ale klientem jest model/agent, więc granice bezpieczeństwa są ostrzejsze.
```

## Faza 11: Secret Manager Integration

Cel: dodać bezpieczny model sekretów.

### Zakres

- `SecretProvider` port,
- fake provider dla testów,
- env provider dla lokalnego dev,
- Bitwarden Secrets Manager adapter,
- audit secret resolution,
- policy/HITL dla wysokiego ryzyka.

### Publiczne commity

1. `feat(secrets): add SecretProvider port`
2. `test(secrets): add fake secret provider`
3. `feat(secrets): add Bitwarden adapter`
4. `security(secrets): audit secret resolution`

### Wiedza do opanowania

- secret manager basics,
- dependency inversion,
- provider adapters,
- nie-logowanie sekretów,
- rotacja i scope tokenów.

### Sygnał dla rekrutera

Projekt pokazuje dojrzałość security, a nie `.env` jako jedyną strategię.

### Kryterium ukończenia

- domena nie zna Bitwardena,
- testy nie używają realnych sekretów,
- sekrety nie są logowane,
- adapter jest opcjonalny i konfigurowalny.

### Referencje do PHP

```text
SecretProvider port jest odpowiednikiem zależności od interfejsu do sekretów,
a Bitwarden adapter jest konkretną implementacją.

Podobnie jak w PHP nie chcesz, żeby kod domenowy znał `.env` albo klienta Vaulta,
tak tutaj domena nie zna Bitwardena.
```

## Faza 12: Minimal Operator Demo

Cel: dodać minimalny interfejs demonstracyjny dla człowieka zatwierdzającego, bez robienia z UI głównego projektu.

### Zakres

- Streamlit, server-rendered UI albo bardzo prosty frontend,
- lista pending requests,
- approve/reject,
- widok audit trail,
- widok traces/eval summaries,
- Playwright tests opcjonalnie, jeśli UI stanie się publicznym demo.

### Publiczne commity

1. `feat(demo): add minimal operator console`
2. `test(e2e): cover approve and reject flow` opcjonalnie

### Wiedza do opanowania

- minimalny operator UX,
- UX approval gates,
- podstawy Playwright opcjonalnie,
- bezpieczeństwo akcji w UI.

### Sygnał dla rekrutera

Projekt jest możliwy do pokazania na demo, ale nie traci focusu AI Engineer na rzecz frontendu.

### Kryterium ukończenia

- da się przejść approval flow w UI,
- UI jest opcjonalne i ma mały zakres,
- UI nie pokazuje sekretów.

### Referencje do PHP

```text
To nie ma być pełny panel administracyjny jak w Symfony EasyAdmin/Nova.
To minimalny operator console pokazujący HITL flow.
```

## Faza 13: Portfolio Polish

Cel: przygotować projekt do oglądania przez rekrutera.

### Zakres

- finalny README,
- architecture diagrams,
- screenshots/GIF,
- public ROADMAP,
- threat model summary,
- demo script,
- "what I learned" sekcja,
- krótkie ADR-y.

### Publiczne commity

1. `docs: add architecture overview`
2. `docs: add demo walkthrough`
3. `docs: add roadmap and learning notes`

### Wiedza do opanowania

- techniczna komunikacja,
- storytelling portfolio,
- diagramy Mermaid,
- opisy tradeoffów.

### Sygnał dla rekrutera

Projekt jest łatwy do oceny w 5-10 minut.

### Kryterium ukończenia

- README prowadzi rekrutera,
- demo działa,
- CI przechodzi,
- architektura jest zrozumiała,
- ryzyka są uczciwie opisane.

## Co z macOS local runtime?

Obecny macOS local runtime nie powinien być głównym nurtem projektu.

Możliwe opcje:

### Opcja A: odłożyć do `.dev/research`

Najbezpieczniejsze teraz. Zachowujemy wiedzę, ale nie pokazujemy jej publicznie.

### Opcja B: skrócić do optional security appendix

Publicznie pokazujemy tylko mały dokument:

```text
docs/security/optional-macos-runtime.md
```

Bez dużego installera i bez robienia z tego fundamentu projektu.

### Opcja C: wrócić do tego później jako case study

Po zbudowaniu realnego Python core można dodać:

> Optional host-level separation profile for high-risk local agent execution.

Rekomendacja na teraz: **Opcja A**.

## Pierwszy prawdziwy vertical slice

Najlepszy pierwszy slice po planie:

```text
Python tooling
  -> domain ApprovalRequest
  -> tests
  -> FastAPI create/list/approve/reject
  -> in-memory repository
  -> audit event in memory
```

To jest małe, ale mówi wszystko:

- Python,
- typy,
- domena,
- API,
- HITL,
- audit,
- testy.

## Rytm pracy

Proponowany rytm:

1. Prywatne wyjaśnienie teorii w `.dev`.
2. Mały publiczny plan lub issue.
3. Implementacja minimalnego slice.
4. Testy.
5. Krótka dokumentacja publiczna.
6. Review: czy to wzmacnia kandydaturę?
7. Commit.

## Pytania do decyzji przed implementacją

1. Czy używamy `uv` od razu?
2. Czy FastAPI ma być w pierwszym technicznym commicie, czy dopiero po domenie?
3. Czy zaczynamy od czystych klas domenowych, czy od Pydantic models?
4. Czy PostgreSQL wchodzi przed LangGraph, czy po pierwszym in-memory workflow?
5. Czy Qdrant i pgvector pokazujemy oba, czy jeden jako główny, drugi jako adapter opcjonalny?
6. Czy publiczny `ROADMAP.md` robimy przed kodem, czy dopiero po pierwszym vertical slice?
7. Czy obecne `docs/` i `install/` usuwamy z working tree, czy przenosimy do `.dev/research`?

## Moja wstępna rekomendacja kolejności

1. Przenieść obecne `docs/` i `install/` do `.dev/research/macos-runtime-experiment/` albo usunąć z working tree.
2. Zrobić prywatną decyzję: "macOS runtime is research, not platform foundation".
3. Zacząć publicznie od `pyproject.toml`, `uv`, `ruff`, `mypy`, `pytest`.
4. Dodać czysty model domenowy approval.
5. Dodać FastAPI boundary.
6. Dopiero później publikować szerszą roadmapę, już opartą o działający core.
