<link rel="stylesheet" href="../styles/main.css">

# Faza 10: MCP Integration And External Tool Context

[← Indeks planowania](README.md) | [Roadmapa](roadmap-draft.md) | [MCP](../technologies/MCP.md) | [Tool Use](../technologies/ToolUse.md) | [Guardrails](../technologies/Guardrails.md) | [Prompt Injection](../technologies/PromptInjection.md)

Status: draft prywatny

Cel fazy: dodać kontrolowany sposób wystawiania narzędzi i zasobów przez MCP bez obchodzenia policy, approval i audit.

## Główna idea

MCP jest adapterem do świata narzędzi, nie domeną.

```text
MCP tool call -> adapter -> application use case -> domain policy -> audit
```

## Zakres techniczny

- minimalny MCP server/client,
- tool exposure,
- allowlist narzędzi,
- policy check przed wykonaniem,
- audit tool call,
- test allowed/denied.

## Czego nie robimy w tej fazie

- szerokiego marketplace narzędzi,
- automatycznego dostępu do hosta,
- sekretów w tool context,
- bypassu HITL.

## Checklist

- [ ] 1. Spike MCP: minimal server/client.
- [ ] 2. Zdefiniować jedno bezpieczne narzędzie read-only.
- [ ] 3. Podpiąć tool call do application use case.
- [ ] 4. Dodać policy przed wykonaniem toola.
- [ ] 5. Dodać audit tool call.
- [ ] 6. Dodać test denied tool call.
- [ ] 7. Udokumentować różnicę Action vs Tool.

## Referencje do PHP

### MCP vs plugin/API dla zewnętrznego klienta

MCP można porównać do plugin API, ale klientem jest agent/model.

```text
PHP:
Wystawiasz endpoint albo command dla znanego klienta.

MCP:
Wystawiasz narzędzie, które może wywołać agent w trakcie reasoning loop.
```

```php
// PHP — endpoint dla zewnętrznego klienta
#[Route('/api/reports/{id}', methods: ['GET'])]
public function show(string $id): JsonResponse
{
    return new JsonResponse($this->reports->get($id));
}
```

```python
# Python/MCP — tool musi nadal przejść przez policy
async def read_report(report_id: str) -> Report:
    command = ReadReportCommand(report_id=report_id)
    return use_case.execute(command)
```

**Implikacje dla AI:**

- Tool nie jest automatycznie bezpieczny.
- Agent może próbować wywołać tool w złym kontekście.
- MCP adapter musi respektować policy i audit.

## Oczekiwany rezultat fazy

System pokazuje nowoczesny tool context, ale nadal kontrolowany przez governance.
