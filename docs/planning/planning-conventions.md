<link rel="stylesheet" href="../styles/main.css">

# Konwencje planowania prywatnego

[← Indeks planowania](README.md) | [Roadmapa](roadmap-draft.md) | [PHP → Python](../technologies/PHP-do-Python.md)

Status: prywatne zasady robocze

Ten dokument opisuje, jak prowadzić prywatne plany w `.dev/planning`, aby wspierały jednocześnie rozwój portfolio i naukę przejścia z PHP/backend engineeringu do AI Engineeringu w Pythonie.

## Sekcja `Referencje do PHP`

Jeśli w planie fazy pojawia się temat, który można sensownie wyjaśnić przez analogię do PHP, dodajemy stałą sekcję:

- nagłówek: `## Referencje do PHP`,
- pod nim jeden lub kilka porównań w stylu dokumentu [PHP → Python](../technologies/PHP-do-Python.md),
- każde porównanie powinno mieć krótką tezę, blok modelu mentalnego, przykład PHP, przykład Python i implikacje.

Preferowany format:

````markdown
### Nazwa porównania

Krótka teza: co dokładnie może pójść źle albo co trzeba zrozumieć.

```text
PHP:
...

Python:
...
```

```php
// PHP — ...
```

```python
# Python — ...
```

**Implikacje dla Python:**
- ...
- ...
````

Sekcja ma pomagać w szybkim przełożeniu nowego pojęcia na znany model mentalny.

Nie dodajemy analogii na siłę. Dodajemy ją wtedy, gdy:

- Pythonowy koncept ma podobieństwo do znanego wzorca z PHP,
- Pythonowy koncept różni się od PHP w sposób groźny dla architektury,
- różnica może być pytaniem na rozmowie technicznej,
- analogia pomaga uniknąć błędnego przeniesienia nawyku z PHP.

## Dobre tematy do referencji PHP

- `pyproject.toml` vs `composer.json`,
- `Protocol` vs interface,
- FastAPI routes vs controllers,
- Pydantic schemas vs DTO/FormRequest/Validator,
- SQLAlchemy repository adapter vs Doctrine repository,
- long-running Python process vs PHP-FPM request lifecycle,
- async/event loop vs klasyczny request-response,
- pytest fake objects vs ręczne test doubles w PHPUnit,
- dependency injection bez kontenera frameworka,
- migrations Alembic vs Doctrine migrations,
- application service/use case vs service class.

## Tematy, których nie tłumaczyć przez PHP na siłę

- attention mechanism,
- embeddings,
- vector search,
- LangGraph node semantics,
- prompt injection,
- LLM evals,
- MCP,
- model context window.

Dla tych tematów można używać analogii tylko jako punktu startowego, ale trzeba szybko przejść do natywnego modelu AI/Python.

## Preferowana struktura prywatnego planu fazy

```markdown
# Faza N: Nazwa

Status: ...

Cel fazy: ...

## Główna idea

## Zakres techniczny

## Co ćwiczymy w Pythonie

## Decyzje architektoniczne

## Checklist

## Referencje do PHP

Jeśli dodajesz tę sekcję do planu fazy, używaj stylu:

- najpierw model mentalny,
- potem kod PHP,
- potem kod Python,
- potem implikacje.

Nie ograniczaj się do samego opisu tekstowego, jeśli da się pokazać kontrast kodem.

## Oczekiwany rezultat fazy
```

## Zasada najważniejsza

Referencje do PHP mają być pomostem, nie kotwicą.

Cel nie brzmi:

```text
Pisać Python tak jak PHP.
```

Cel brzmi:

```text
Użyć 20 lat doświadczenia backendowego jako akceleratora,
ale nauczyć się idiomatycznego Pythona i architektury AI-native.
```
