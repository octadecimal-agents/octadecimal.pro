import json
import os
from pathlib import Path

from dotenv import load_dotenv

from pipecat_translator.rag.embedder import Embedder
from pipecat_translator.rag.store import VectorStore

load_dotenv()


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY is required")
        return

    seed_path = Path(__file__).parent.parent / "src" / "pipecat_translator" / "rag" / "seed_phrases.json"
    with open(seed_path) as f:
        phrases = json.load(f)

    embedder = Embedder(api_key=api_key)
    store = VectorStore(embedder=embedder)

    sample_texts = [p["pl"] + " " + p["en"] for p in phrases[:3]]
    store.initialize(sample_texts)
    store.upsert(phrases)

    print(f"Zaindeksowano {len(phrases)} fraz do Qdrant (in-memory)")

    test = store.search("potrzebuje wiecej czasu na analize")
    print(f"\nTest wyszukiwania dla 'potrzebuje wiecej czasu na analize':")
    for r in test:
        print(f"  [{r.topic}] ({r.score:.3f}) {r.text}")


if __name__ == "__main__":
    main()
