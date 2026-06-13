# Pipecat Translator — Test Plan

## macOS-native E2E tests using `say` + `screencapture`

### Available macOS tools

| Narzędzie | Polecenie | Zastosowanie |
|-----------|-----------|-------------|
| **TTS** | `say -v Zosia -o pl.wav "tekst"` | Generowanie PL audio |
| | `say -v Samantha -o en.wav "text"` | Generowanie EN audio |
| **Screenshot** | `screencapture -x -R<x,y,w,h> shot.png` | Przechwytywanie overlay'u |
| **WAV** | Python `wave` module | Odczytywanie/analiza audio |

### Struktura testów

```
tests/
├── unit/
│   ├── test_config.py        # Walidacja configu, brakujących kluczy
│   └── test_rag.py           # VectorStore: indexowanie + semantic search
├── integration/
│   ├── test_poc.py           # Phase 0: tłumaczenie tekstowe przez LLM
│   └── test_pipeline.py      # Phase 1: pipeline z mock STT/TTS
├── e2e/
│   ├── test_audio_pipeline.sh # Phase 1b: generuj audio → pipeline → wynik
│   ├── test_overlay.sh        # Phase 2: screenshot overlay'u
│   └── test_rag_search.sh     # Phase 3: wyszukiwanie semantyczne
├── data/
│   └── fixtures.json          # Testowe frazy PL↔EN
└── run_all.sh                 # Runner uruchamiający wszystkie testy
```

### Przebieg testów

#### 1. Unit: Config (`test_config.py`)
- `test_missing_api_key` — Config.validate() zwraca błąd dla pustego OPENAI_API_KEY
- `test_valid_config` — Config z kluczem przechodzi walidację

#### 2. Unit: RAG (`test_rag.py`)
- `test_embed_and_search` — Indeksuje 3 frazy, szuka najbliższej, sprawdza score > 0.5
- `test_search_before_init` — Search na niezainicjalizowanym store zwraca []

#### 3. Integration: PoC (`test_poc.py`)
- `test_translate_and_suggest` — Woła TranslatorPOC.translate_and_suggest() z tekstem testowym
- Sprawdza czy wynik zawiera "translation" i "suggestion"

#### 4. Integration: Pipeline (`test_pipeline.py`)
- `test_pipeline_build` — Tworzy pipeline z build_translation_pipeline()
- Sprawdza czy pipeline jest Pipeline + ma odpowiednią liczbę processorów

#### 5. E2E: Audio (`test_audio_pipeline.sh`)
```
1. say -v Zosia -o /tmp/test_pl.wav "Dzień dobry, jak się masz?"
2. say -v Samantha -o /tmp/test_en.wav "Hello, how are you?"
3. Weryfikacja: oba pliki istnieją, mają > 0 bajtów, format WAV
```

#### 6. E2E: Overlay (`test_overlay.sh`)
```
1. Uruchom run_speech.py w tle
2. Poczekaj 5s na inicjalizację
3. screencapture -x /tmp/overlay_test.png
4. Sprawdź czy plik istnieje i ma > 10KB
5. Zabij proces run_speech.py
```

#### 7. E2E: RAG search (`test_rag_search.sh`)
```
1. Uruchom scripts/seed_rag.py
2. Sprawdź output: "Zaindeksowano 31 fraz"
3. Sprawdź wyniki wyszukiwania dla "potrzebuje wiecej czasu"
4. Weryfikacja: pierwszy wynik zawiera "Potrzebujemy więcej czasu"
```

### Wymagania środowiskowe

- **macOS** z `say` i `screencapture` (domyślnie dostępne)
- Python 3.11+ z zainstalowanymi zależnościami (`uv sync`)
- Zmienna `OPENAI_API_KEY` w `.env`
- Dla testów audio: mikrofon/głośnik (niewymagane dla testów jednostkowych)
