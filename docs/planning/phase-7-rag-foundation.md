<link rel="stylesheet" href="../styles/main.css">

# Faza 7: RAG Foundation

[← Indeks planowania](README.md) | [Roadmapa](roadmap-draft.md) | [RAG](../technologies/RAG.md) | [Embeddings](../technologies/Embeddings.md) | [Qdrant](../technologies/Qdrant.md) | [pgvector](../technologies/pgvector.md) | [LLM Evals](../technologies/LLMEvals.md)

Status: draft prywatny

Cel fazy: dodać kontrolowany subsystem wiedzy, który może zasilać workflow kontekstem bez mieszania retrieval z domeną governance.

## Główna idea

RAG to pipeline:

```text
documents -> chunks -> embeddings -> vector store -> retrieval -> context
```

Nie jest to “wrzuć PDF do promptu”.

## Zakres techniczny

- testowe dokumenty publiczne/syntetyczne,
- ingestion command/use case,
- chunking,
- embedding port,
- retriever port,
- Qdrant albo pgvector jako pierwszy adapter,
- testy retrieval,
- metadata.

## Czego nie robimy w tej fazie

- pełnej produkcyjnej jakości RAG,
- rerankingu, jeśli nie jest potrzebny do slice'a,
- agentic RAG,
- MCP,
- UI do uploadu dokumentów.

## Checklist

- [ ] 1. Wybrać pierwszy backend: Qdrant albo pgvector.
- [ ] 2. Dodać syntetyczny dataset.
- [ ] 3. Zaprojektować `DocumentChunk`.
- [ ] 4. Dodać `EmbeddingProvider` port.
- [ ] 5. Dodać `Retriever` port.
- [ ] 6. Dodać ingestion use case.
- [ ] 7. Dodać retrieval use case.
- [ ] 8. Dodać adapter backendu.
- [ ] 9. Dodać test jakości retrieval.
- [ ] 10. Udokumentować tradeoff Qdrant vs pgvector.

## Referencje do PHP

### RAG vs Elasticsearch indexing

Najbliższe znane skojarzenie to indeksowanie do wyszukiwarki, ale semantyka jest inna.

```text
PHP:
Encje -> Elasticsearch index -> keyword/full-text search

RAG:
Dokumenty -> chunks -> embeddings -> vector search -> context dla LLM
```

```php
// PHP — klasyczny search index
$client->index([
    'index' => 'docs',
    'body' => ['title' => $title, 'content' => $content],
]);
```

```python
# Python — ingestion RAG zapisuje wektory i metadata
chunk = DocumentChunk(text=text, metadata=metadata)
embedding = embedding_provider.embed(chunk.text)
vector_store.upsert(chunk_id=chunk.id, vector=embedding, metadata=chunk.metadata)
```

**Implikacje dla Python:**

- Chunking jest decyzją jakościową, nie detalem technicznym.
- Metadata decydują o filtrowaniu i audycie.
- Retrieved context może być niebezpieczny, bo trafi do promptu.

## Oczekiwany rezultat fazy

System potrafi pobrać kontrolowany kontekst z dokumentów i zrobić to przez porty, nie przez bezpośrednie wywołania vector DB z use case'a agentowego.
