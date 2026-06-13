import os
import sys

sys.path.insert(0, "src")

import pytest

from pipecat_translator.rag.embedder import Embedder
from pipecat_translator.rag.store import VectorStore

API_KEY = os.getenv("OPENAI_API_KEY", "")

pytestmark = pytest.mark.skipif(not API_KEY, reason="OPENAI_API_KEY required")


@pytest.fixture
def store():
    embedder = Embedder(api_key=API_KEY)
    vs = VectorStore(embedder=embedder)
    vs.initialize(["test phrase one", "test phrase two"])
    vs.upsert([
        {"pl": "Dzień dobry", "en": "Good morning", "topic": "powitanie"},
        {"pl": "Jak się masz?", "en": "How are you?", "topic": "powitanie"},
        {"pl": "Potrzebuję więcej czasu", "en": "I need more time", "topic": "terminy"},
    ])
    return vs


def test_search_returns_results(store):
    results = store.search("cześć jak leci", top_k=2)
    assert len(results) > 0
    assert all(r.score > 0 for r in results)


def test_search_returns_pl(store):
    results = store.search("dzień dobry", top_k=1)
    assert len(results) >= 1
    assert "Dzień dobry" in results[0].pl


def test_search_before_init_returns_empty():
    embedder = Embedder(api_key=API_KEY)
    vs = VectorStore(embedder=embedder)
    assert vs.search("test") == []


def test_result_fields(store):
    results = store.search("time deadline", top_k=1)
    r = results[0]
    assert r.pl
    assert r.en
    assert r.topic
    assert r.score > 0
