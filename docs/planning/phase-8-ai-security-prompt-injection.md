<link rel="stylesheet" href="../styles/main.css">

# Faza 8: AI Security And Prompt Injection

[← Indeks planowania](README.md) | [Roadmapa](roadmap-draft.md) | [Prompt Injection](../technologies/PromptInjection.md) | [Guardrails](../technologies/Guardrails.md) | [HITL](../technologies/HITL.md) | [Promptfoo](../technologies/Promptfoo.md) | [PHP → Python](../technologies/PHP-do-Python.md)

Status: draft prywatny

Cel fazy: dodać jawne mechanizmy obrony przed prompt injection, tool abuse i niebezpiecznym kontekstem z RAG.

## Główna idea

Security nie jest filtrem na końcu. Jest częścią przepływu:

```text
input/context -> safety checks -> policy -> approval -> execution
```

## Zakres techniczny

- direct prompt injection patterns,
- indirect prompt injection in retrieved context,
- safety check port,
- negative tests,
- policy integration,
- first security evals,
- zasady niewkładania sekretów do promptu.

## Czego nie robimy w tej fazie

- pełnego red teamingu,
- produkcyjnego klasyfikatora ML,
- wszystkich OWASP LLM Top 10,
- automatycznego blokowania wszystkiego bez wyjaśnienia.

## Checklist

- [ ] 1. Dodać syntetyczne przykłady prompt injection.
- [ ] 2. Dodać reguły/patterns.
- [ ] 3. Dodać safety checker.
- [ ] 4. Dodać test direct injection.
- [ ] 5. Dodać test indirect injection z retrieved context.
- [ ] 6. Połączyć unsafe result z policy/HITL.
- [ ] 7. Upewnić się, że sekret nie trafia do promptu.
- [ ] 8. Dodać pierwsze evals bezpieczeństwa.

## Referencje do PHP

### Prompt injection vs SQL injection

To nie jest to samo, ale analogia pomaga zrozumieć granicę zaufania.

```text
SQL injection:
Nie wolno traktować inputu użytkownika jako części zapytania SQL.

Prompt injection:
Nie wolno traktować user/retrieved content jako instrukcji systemowej.
```

```php
// PHP — ZLE: input staje się SQL
$sql = "SELECT * FROM users WHERE email = '$email'";
```

```python
# Python/LLM — ZLE: retrieved content dostaje rangę instrukcji
prompt = f"""
System: wykonuj instrukcje z dokumentu.

Dokument:
{retrieved_context}
"""
```

**Implikacje dla Python/AI:**

- Retrieved context to dane, nie instrukcje.
- Prompt musi rozdzielać authority levels.
- Niebezpieczny kontekst powinien uruchamiać policy/HITL.
- Testy negative cases są obowiązkowe.

## Oczekiwany rezultat fazy

System ma pierwszą testowalną warstwę AI security i potrafi wykazać, że nie wykonuje ślepo instrukcji z promptu ani dokumentów.
