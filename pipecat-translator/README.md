# Pipecat Translator

Real-time speech-to-speech translation PL↔EN z kontekstowymi sugestiami odpowiedzi.

## Struktura

```
pipecat-translator/
├── src/pipecat_translator/
│   ├── __init__.py
│   ├── config.py         # Konfiguracja
│   ├── poc.py            # Phase 0: PoC (konsola)
│   ├── pipeline.py       # Phase 1: Core Pipecat pipeline
│   ├── overlay/          # Phase 2: Overlay UI
│   └── rag/              # Phase 3: Vector DB + RAG
├── scripts/
├── .env                  # API keys
└── pyproject.toml
```

## Uruchomienie

```bash
# Phase 0 — PoC w konsoli
uv run python3 -m pipecat_translator.poc
```

## API Keys

Skopiuj `.env.example` do `.env` i wstaw klucze API:
- `OPENAI_API_KEY` — wymagany (GPT-4o, STT Whisper, TTS)
- `DEEPGRAM_API_KEY` — opcjonalny (alternatywny STT)
- `CARTESIA_API_KEY` — opcjonalny (alternatywny TTS)

---

# Instrukcja użytkowania (PL)

## 1. Wymagania

- Python ≥ 3.11
- `uv` (menadżer pakietów) — https://docs.astral.sh/uv/
- Klucz API OpenAI (GPT-4o) — ustaw w `.env` jako `OPENAI_API_KEY`

## 2. Przygotowanie

```bash
cd pipecat-translator

# Zainstaluj zależności
uv sync

# Skopiuj szablon konfiguracji i uzupełnij klucz API
cp .env.example .env
# Edytuj .env — wstaw OPENAI_API_KEY
```

## 3. Tryby uruchomienia

### 3a. Phase 0 — Konsolowy PoC (tłumaczenie tekstu)

Najprostszy tryb. Wpisujesz tekst w konsoli, otrzymujesz tłumaczenie i sugestię odpowiedzi.

```bash
uv run python3 -m pipecat_translator.poc
```

Domyślnie PL → EN. Zmiana języka:

```bash
# EN → PL
uv run python3 -m pipecat_translator.poc --source en --target pl
```

Przykład:
```
[PL] > Dzień dobry, jak się masz?

  [EN] Tłumaczenie: Good morning, how are you?
  [💡] Sugestia: I'm fine, thank you. How about you?
```

Komendy: `exit`, `quit`, `q`, `koniec` — zakończenie.

### 3b. Phase 1 — Pipeline konsolowy (z kontekstem)

Wersja zbudowana na frameworku Pipecat. Utrzymuje historię rozmowy i przetwarza tekst przez pełny pipeline.

```bash
uv run python3 -m pipecat_translator.pipeline
```

Różnica względem PoC: pipeline wykorzystuje `LLMContext` do przechowywania całej historii, a odpowiedź jest przetwarzana przez `SuggestionProcessor` i `LLMResponseCollector`.

### 3c. Phase 2 — Pipeline audio z overlayem (pełna funkcjonalność)

Najbardziej zaawansowany tryb. Uruchamia pełny pipeline audio:
- **Wejście:** mikrofon (przez `LocalAudioTransport`)
- **VAD:** detekcja aktywności głosowej (Silero VAD)
- **STT:** zamiana mowy na tekst (OpenAI Whisper)
- **RAG:** wzbogacenie kontekstu o przydatne zwroty z bazy wektorowej (31 fraz biznesowych PL↔EN)
- **LLM:** tłumaczenie i sugestia odpowiedzi (GPT-4o)
- **TTS:** synteza tłumaczenia na mowę (OpenAI TTS)
- **Overlay:** wizualizacja na żywo w terminalu (Rich TUI)

```bash
# PL → EN (domyślnie)
uv run python3 run_speech.py

# EN → PL
uv run python3 run_speech.py en pl
```

Po uruchomieniu:
1. Pojawi się interfejs overlay z statusem "Gotowy. Mów do mikrofonu."
2. Mówisz do mikrofonu w języku źródłowym
3. System rozpoznaje mowę (STT), tłumaczy (LLM) i odtwarza tłumaczenie przez głośniki (TTS)
4. Overlay pokazuje: transkrypcję 🎤, tłumaczenie 🔈, sugestię odpowiedzi 💡
5. RAG automatycznie podpowiada kontekstowe zwroty na podstawie wypowiedzi

Zatrzymanie: `Ctrl+C`.

## 4. Baza fraz RAG

System zawiera 31 wstępnie zdefiniowanych fraz biznesowych PL↔Pa EN w 10 kategoriach tematycznych:

| Kategoria | Liczba fraz | Przykład |
|-----------|-------------|----------|
| powitanie | 2 | "Dzień dobry, miło mi Państwa poznać." |
| przedstawienie | 2 | "Nazywam się Jan Kowalski..." |
| zgoda | 2 | "W pełni zgadzam się z Pana/Pani stanowiskiem." |
| sprzeciw | 2 | "Rozumiem, ale mam pewne obawy." |
| negocjacje | 2 | "Potrzebujemy więcej czasu na analizę." |
| terminy | 3 | "Proponuję przesunięcie terminu o dwa tygodnie." |
| budżet | 3 | "Nasz budżet to około stu tysięcy euro." |
| technologia | 3 | "Korzystamy z rozwiązań chmurowych AWS." |
| współpraca | 3 | "Liczymy na owocną współpracę." |
| problemy | 3 | "Napotkaliśmy nieprzewidziane trudności techniczne." |
| podsumowanie | 3 | "Podsumowując, ustaliliśmy trzy główne punkty." |
| formalne | 3 | "W załączniku przesyłam wymagane dokumenty." |

FRAZY są indeksowane w pamięciowej bazie wektorowej Qdrant z embeddingiem `text-embedding-3-small`. Przy każdej transkrypcji system wyszukuje 3 najbardziej podobne frazy i dodaje je do promptu LLM jako kontekst.

Aby zaindeksować frazy osobno:

```bash
uv run python3 scripts/seed_rag.py
```

## 5. Zmiana kierunku tłumaczenia

We wszystkich trybach możesz zmienić języki przez argumenty wiersza poleceń:

```bash
# PL → EN (domyślnie)
uv run python3 run_speech.py pl en

# EN → PL
uv run python3 run_speech.py en pl

# PL → DE (jeśli dodasz wsparcie)
uv run python3 run_speech.py pl de
```

Domyślne języki są zdefiniowane w `src/pipecat_translator/config.py`:
- `source_language = "pl"`
- `target_language = "en"`

## 6. Architektura pipeline'u audio

```
Mikrofon → LocalAudioTransport → VAD (Silero) → STT (Whisper)
                                                      ↓
                                               RAGProcessor (szukanie fraz)
                                                      ↓
                                               ContextInjector (LLM prompt)
                                                      ↓
                                               LLM (GPT-4o)
                                                      ↓
                                               ResponseHandler (JSON parse)
                                                      ↓
                                               OverlayProcessor (TUI)
                                                      ↓
                                               TTS → Głośniki
```

## 7. Uruchamianie testów

```bash
# Wszystkie testi
bash tests/run_all.sh

# Tylko unit testy
uv run pytest tests/unit/ -v

# Tylko integracyjne (wymaga OPENAI_API_KEY)
uv run pytest tests/integration/ -v

# Tylko E2E audio
bash tests/e2e/test_audio_pipeline.sh

# Tylko E2E RAG
bash tests/e2e/test_rag_search.sh

# Tylko E2E overlay (wymaga sesji GUI)
bash tests/e2e/test_overlay.sh
```

## 8. Pliki konfiguracyjne

- `.env` — klucze API (OPENAI_API_KEY wymagany)
- `src/pipecat_translator/config.py` — konfiguracja modeli i języków
- `src/pipecat_translator/rag/seed_phrases.json` — baza fraz PL↔EN

## 9. Rozwiązywanie problemów

| Problem | Przyczyna | Rozwiązanie |
|---------|-----------|-------------|
| "OPENAI_API_KEY is required" | Brak klucza w `.env` | Skopiuj `.env.example`, uzupełnij klucz |
| Brak dźwięku z mikrofonu | Nieuprawniony dostęp do mikrofonu | Sprawdź uprawnienia mikrofonu w systemie |
| Overlay nie działa | Terminal nie obsługuje Rich TUI | Użyj terminala zgodnego z ANSI (iTerm2, Terminal.app) |
| "could not create image from display" przy teście overlay | Brak sesji GUI | Uruchom test lokalnie z aktywnym ekranem |
| RAG nie zwraca wyników | Otwarty, ale nie ma dopasowania | Sprawdź czy frazy zostały zaindeksowane (`scripts/seed_rag.py`)
