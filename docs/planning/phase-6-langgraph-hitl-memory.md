<link rel="stylesheet" href="../styles/main.css">

# Faza 6: LangGraph HITL Workflow And Agent Memory

[← Indeks planowania](README.md) | [Roadmapa](roadmap-draft.md) | [LangGraph](../technologies/LangGraph.md) | [Agent Memory](../technologies/AgentMemory.md) | [HITL](../technologies/HITL.md) | [Tool Use](../technologies/ToolUse.md) | [PHP → Python](../technologies/PHP-do-Python.md)

Status: draft prywatny

Cel fazy: zbudować pierwszy realny agentic workflow z kontrolą policy, przerwaniem na approval i możliwością wznowienia.

## Główna idea

LangGraph nie zastępuje domeny ani application. Jest adapterem/orchestrator workflow:

```text
LangGraph node -> application use case -> domain policy -> approval/audit ports
```

## Zakres techniczny

- minimalny state,
- node proponujący action,
- node policy check,
- conditional routing,
- HITL interrupt,
- resume po decyzji,
- checkpointing jako short-term memory,
- test workflow.

## Co ćwiczymy w Pythonie

- typed state,
- funkcje jako nodes,
- conditional edges,
- long-running workflow,
- testowanie workflow,
- granica między state a audit trail.

## Czego nie robimy w tej fazie

- multi-agent systemu,
- RAG,
- pamięci semantycznej,
- realnego LLM reasoning loop,
- MCP.

## Checklist

- [ ] 1. Spike LangGraph: 3 nodes, conditional edge, interrupt/resume.
- [ ] 2. Dodać minimalny workflow state.
- [ ] 3. Dodać node tworzący/proponujący `Action`.
- [ ] 4. Dodać node wywołujący `RequestActionUseCase`.
- [ ] 5. Dodać routing `ALLOW/DENY/REQUIRE_APPROVAL`.
- [ ] 6. Dodać HITL pause.
- [ ] 7. Dodać resume po approval.
- [ ] 8. Dodać checkpointing.
- [ ] 9. Zapisywać audit eventy.
- [ ] 10. Dodać test flow.

## Referencje do PHP

### LangGraph vs workflow/state machine

Najbliższa analogia z PHP to workflow component albo state machine, nie kontroler.

```text
PHP:
Workflow zwykle przełącza encję między stanami.

LangGraph:
Workflow przełącza stan procesu agentowego między node'ami.
```

```php
// PHP — state machine wokół encji
$workflow->apply($approvalRequest, 'approve');
```

```python
# Python — graph node przetwarza state i zwraca nowy state
def policy_node(state: WorkflowState) -> WorkflowState:
    result = use_case.execute(state.command)
    return replace(state, policy_result=result)
```

**Implikacje dla Python:**

- Node nie powinien zawierać całej logiki biznesowej.
- Node jest krokiem workflow, use case nadal robi proces.
- Checkpoint to pamięć procesu, nie zamiennik audit loga.

### Checkpointing vs sesja/request

```text
PHP:
Request kończy się szybko, stan długiego procesu trzeba zapisać samemu.

LangGraph:
Checkpoint pozwala wznowić proces agentowy po przerwaniu.
```

```php
// PHP — stan trzeba jawnie odłożyć w DB/session/queue
$repository->save($processState);
```

```python
# Python — checkpointing zapisuje stan grafu do wznowienia
graph.invoke(input_state, config={"configurable": {"thread_id": thread_id}})
```

**Implikacje dla Python:**

- Checkpointing to short-term memory workflow.
- Audit trail nadal musi być osobnym, trwałym śladem.
- Resume musi być testowalne.

## Oczekiwany rezultat fazy

Projekt staje się realnie agentic: istnieje workflow, który zatrzymuje się na decyzji człowieka i nie obchodzi policy.
