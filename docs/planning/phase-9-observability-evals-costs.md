<link rel="stylesheet" href="../styles/main.css">

# Faza 9: Observability, Evals And Cost Monitoring

[← Indeks planowania](README.md) | [Roadmapa](roadmap-draft.md) | [Langfuse](../technologies/Langfuse.md) | [OpenTelemetry](../technologies/OpenTelemetry.md) | [LLM Evals](../technologies/LLMEvals.md) | [Promptfoo](../technologies/Promptfoo.md) | [Grafana](../technologies/Grafana.md)

Status: draft prywatny

Cel fazy: sprawić, żeby jakość, koszt i zachowanie systemu AI były mierzalne.

## Główna idea

Produkcyjny system AI nie może działać na zasadzie “wydaje się, że odpowiada dobrze”.

```text
workflow -> traces -> metrics -> evals -> regression signal
```

## Zakres techniczny

- trace IDs,
- Langfuse traces,
- OpenTelemetry spans,
- token usage,
- estimated cost per request,
- latency,
- cache hit ratio,
- eval dataset,
- eval runner.

## Czego nie robimy w tej fazie

- pełnego Grafana dashboardu, jeśli nie jest potrzebny,
- production SLO,
- skomplikowanych LLM-as-judge metryk bez walidacji,
- logowania prywatnych danych.

## Checklist

- [ ] 1. Dodać trace id do audit events.
- [ ] 2. Dodać minimalną integrację Langfuse.
- [ ] 3. Dodać OpenTelemetry span dla use case/workflow.
- [ ] 4. Dodać token usage model.
- [ ] 5. Dodać cost estimate.
- [ ] 6. Dodać eval dataset.
- [ ] 7. Dodać eval runner.
- [ ] 8. Dodać test, że sekrety/PII nie trafiają do traces.
- [ ] 9. Dodać README/demo output dla evals.

## Referencje do PHP

### Observability AI vs klasyczne logi/APM

AI observability musi śledzić więcej niż status HTTP.

```text
PHP backend:
status, latency, exception, SQL query count

AI system:
status, latency, prompt version, model, token usage, cost, retrieval context, eval score
```

```php
// PHP — klasyczny log requestu
$logger->info('request handled', [
    'route' => $route,
    'duration_ms' => $duration,
]);
```

```python
# Python/AI — trace musi zawierać metryki LLM
audit_writer.record(
    event_type="llm_call.completed",
    metadata={
        "model": model,
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "estimated_cost_usd": cost,
    },
)
```

**Implikacje dla Python/AI:**

- Koszt requestu nie jest stały.
- Prompt/model/retrieval są częścią debugowania.
- Evals są odpowiednikiem regresji jakościowej, której zwykłe unit testy nie pokryją.

## Oczekiwany rezultat fazy

Projekt pokazuje dojrzałość produkcyjną: można mierzyć jakość, koszt i bezpieczeństwo workflow.
