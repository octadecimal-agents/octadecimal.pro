<link rel="stylesheet" href="../styles/main.css">

# Faza 13: Portfolio Polish

[← Indeks planowania](README.md) | [Roadmapa](roadmap-draft.md) | [GitHub Actions](../technologies/GitHubActions.md) | [LaTeX](../technologies/LaTeX.md) | [Osascript](../technologies/Osascript.md)

Status: draft prywatny

Cel fazy: przygotować projekt do szybkiej, pozytywnej oceny przez rekrutera lub hiring managera.

## Główna idea

Publiczne repo ma opowiadać historię:

```text
security-first agentic AI platform
-> clean Python architecture
-> HITL governance
-> RAG
-> observability/evals/costs
-> audit-ready engineering
```

## Zakres techniczny

- finalny README,
- architecture overview,
- diagramy Mermaid,
- screenshots/GIF,
- public roadmap,
- demo script,
- threat model summary,
- ADR-y,
- sekcja “what I learned”.

## Czego nie robimy w tej fazie

- ukrywania ograniczeń,
- sztucznego marketingu,
- dopisywania nieistniejących funkcji,
- wrzucania prywatnych `.dev` materiałów.

## Checklist

- [ ] 1. README prowadzi rekrutera od problemu do demo.
- [ ] 2. Jest diagram architektury.
- [ ] 3. Jest demo script.
- [ ] 4. Jest jasne “what is implemented”.
- [ ] 5. Jest jasne “what is planned”.
- [ ] 6. Jest threat model summary.
- [ ] 7. CI przechodzi.
- [ ] 8. Nie ma sekretów i prywatnych evidence.
- [ ] 9. Commit historia jest logiczna.

## Referencje do PHP

### Portfolio README vs komercyjna dokumentacja projektu

README portfolio ma być bardziej selektywne niż pełna dokumentacja firmowa.

```text
Projekt firmowy:
README często mówi jak uruchomić projekt i gdzie są moduły.

Portfolio:
README musi też wyjaśnić, dlaczego te decyzje pokazują kompetencje kandydata.
```

```php
// PHP portfolio często pokazuje framework i CRUD
// Symfony + Doctrine + API Platform + tests
```

```python
# AI Engineer portfolio musi pokazać więcej niż framework
# governance + HITL + RAG + evals + observability + security
```

**Implikacje dla projektu:**

- README ma być czytelne w 5-10 minut.
- Trzeba pokazać tradeoffy, nie tylko listę technologii.
- Publiczne docs mają być po angielsku, `.dev` pozostaje prywatne po polsku.

## Oczekiwany rezultat fazy

Repo jest gotowe jako portfolio: da się je szybko zrozumieć, uruchomić i obronić na rozmowie technicznej.
