---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments: []
workflowType: 'research'
lastStep: 1
research_type: 'technical'
research_topic: 'Real-time open source speech-to-speech translation systems for English/Polish communication'
research_goals: '- Identify quality-focused real-time speech-to-speech translation systems
- Evaluate ready-made solutions with extensibility potential
- Include both open source and paid/API-based options
- Focus on English-Polish language pair
- Assess context-aware enhancement possibilities'
user_name: 'CEO'
date: '2026-06-13'
web_research_enabled: true
source_verification: true
---

# Research Report: technical

**Date:** 2026-06-13
**Author:** CEO
**Research Type:** technical

---

## Research Overview

Niniejszy raport dokumentuje kompleksowe badanie techniczne systemów real-time speech-to-speech (S2S) dla komunikacji angielsko-polskiej. Przeprowadzono analizę rynku rozwiązań open-source i komercyjnych, oceniono stack technologiczny (STT, TTS, LLM, frameworki integracyjne) oraz opracowano szczegółowy plan implementacji systemu opartego na frameworku Pipecat z rozszerzeniem o generowanie kontekstowych sugestii odpowiedzi przez RAG/Vector DB. Badanie oparto na weryfikowalnych źródłach webowych z 2025-2026.

---

<!-- Content will be appended sequentially through research workflow steps -->

## Technical Research Scope Confirmation

**Research Topic:** Real-time open source speech-to-speech translation systems for English/Polish communication
**Research Goals:** Identify quality-focused real-time speech-to-speech translation systems, Evaluate ready-made solutions with extensibility potential, Include both open source and paid/API-based options, Focus on English-Polish language pair, Assess context-aware enhancement possibilities

**Technical Research Scope:**

- Architecture Analysis - design patterns, frameworks, system architecture
- Implementation Approaches - development methodologies, coding patterns
- Technology Stack - languages, frameworks, tools, platforms
- Integration Patterns - APIs, protocols, interoperability
- Performance Considerations - scalability, optimization, patterns

**Research Methodology:**

- Current web data with rigorous source verification
- Multi-source validation for critical technical claims
- Confidence level framework for uncertain information
- Comprehensive technical coverage with architecture-specific insights

**Scope Confirmed:** 2026-06-13

## Technology Stack Analysis

### Speech-to-Text (STT) / ASR — Open Source

| Model | Języki | WER (EN) | Latency | Uwagi |
|-------|--------|----------|---------|-------|
| **Whisper Large V3** (OpenAI) | 99+ (w tym PL) | ~5-6% | Medium | Złoty standard multilingual, dobra jakość PL |
| **Whisper Large V3 Turbo** | 99+ | ~5-7% | Niski | 6.3x szybszy od V3 |
| **NVIDIA Canary-Qwen 2.5B** | EN głównie | ~3-4% | Niski | Najlepszy WER dla EN, limited PL |
| **NVIDIA Parakeet TDT 1.1B** | EN | ~7-8% | **Ultra-niski** | Streaming sub-100ms, RTFx >2000 |
| **IBM Granite Speech 3.3 8B** | EN + translation | ~4% | Medium | Enterprise, ASR + translation |
| **Qwen3-ASR** (Alibaba) | 52 języki | ~5% | Niski | Dobry wybór dla PL |
| **Moonshine** | EN | ~6-7% | Bardzo niski | Edge/mobile, mały model |
| **Wav2Vec 2.0 / XLS-R** (Meta) | 128 języków | ~8%+ | Medium | Najlepszy do fine-tuningu na PL |

*Źródło: Northflank Benchmark STT 2026, Gladia.io*

### Text-to-Speech (TTS) — Open Source

| Model | Jakość | Języki | Streaming | Voice Cloning |
|-------|--------|--------|-----------|---------------|
| **Kokoro-82M** | Bardzo dobra | EN, JP, CN, KR, FR, PL | Tak | Nie |
| **ChatTTS** | Dobra | EN, CN | Tak | Nie |
| **Pocket TTS** (Kyutai) | Bardzo dobra | EN, FR | **Tak, streaming** | Tak |
| **Qwen3-TTS** (Alibaba) | Bardzo dobra | EN, CN, JP, KR, FR | Tak | Tak (CustomVoice) |
| **Coqui XTTS** | Dobra | 17 języków (w tym PL) | Ograniczony | Tak (5s próbka) |
| **Cartesia Sonic-3** | Bardzo dobra | 40+ języków (w tym PL) | Tak | Tak (10s próbka) |

*Źródło: Gradium TTS Guide 2026, Speechmatics, Inworld.ai*

## Integration Patterns Analysis — Palabra.ai

### Integration Architecture: Dwie ścieżki

**Ścieżka 1 — Desktop App (no-code, rekomendowana na start)**
```
┌─────────────────────────────────────────────┐
│  Użytkownik A (PL)  ─── Teams/Meet ─── Użytkownik B (CH/EN) │
│         │                                       │
│         ▼                                       │
│  Palabra Desktop App                  Palabra Desktop App    │
│  (nasłuchuje audio systemowe)         (nasłuchuje audio)     │
│         │                                       │
│         └──────── Palabra Cloud ────────────────┘
│           WebSocket / WebRTC streaming
│           <1s latency, 2-way translation
│           Custom glossary applied
└─────────────────────────────────────────────┘
```

- Działa nakładkowo na Teams/Meet — nie wymaga pluginów ani botów
- Jedna subskrypcja dla organizatora
- 60+ języków, custom glossary
- *Źródło: palabra.ai/solutions/ms-teams, palabra.ai/solutions/google-meet*

**Ścieżka 2 — API/SDK (dla rozszerzalności i własnych integracji)**

### API Design Patterns

| Pattern | Palabra Implementation |
|---------|----------------------|
| **WebRTC** (client-side) | `PalabraClient` JS/TS — `startTranslation()`, `startPlayback()` |
| **WebSocket** (server-side) | `wss://` — dedykowany quick start dla backendów |
| **REST** (management) | CRUD dla glossary, sessions, voice cloning |
| **OAuth 2.0** | `clientId` + `clientSecret` → access token, refresh token |
| **Event-driven** | `translation`, `transcription` event emitters |

*Źródło: docs.palabra.ai*

### SDKs & Client Libraries

| Język | Pakiet | Zastosowanie |
|-------|--------|-------------|
| **Python** | `palabra-ai` (PyPI) | Backend, server-side, automatyzacja |
| **JavaScript/TypeScript** | `@palabra-ai/translator` (npm) | Web apps, Electron, desktop |
| **Java** | `palabra-ai-java` (GitHub) | Android, enterprise backend |

### Audio Streaming Protocol

```
Browser/client → getUserMedia → WebRTC PeerConnection
                              → audio stream opus encoded
                              → Palabra Cloud (WebSocket/WebRTC)
                              → STT → Translation → TTS
                              → translated audio stream ←
                              → speaker output
```

- **Codec:** Opus (WebRTC), PCM/WAV (WebSocket raw audio)
- **Latency:** <1s end-to-end (sub-second)
- **Bandwidth:** 10–20 Kb/s (minimum dla stabilnej translacji)
- **Auto language detection** — opcjonalna, wykrywa zmianę języka w trakcie rozmowy

### Glossary Integration (klucz dla Twojego use-case'a)

| Typ Glossary | Działanie | Przykład |
|-------------|-----------|----------|
| **Translation** | Termin w języku A → termin w języku B | "Zalecenie inwestycyjne" → "Investment recommendation" |
| **Validation** | Potwierdza, że termin został poprawnie rozpoznany | Weryfikuje "EBITDA" jako poprawny termin |
| **Recognition** | Poprawia ASR dla specyficznych terminów | Uczy model rozpoznawać "Schengen" zamiast "shen-gen" |

**Implementacja glossary:**
- Upload CSV (max 1MB) przez Web UI lub API
- Przypisanie do language pair (np. PL→EN)
- Automatycznie aktywne we wszystkich aplikacjach Palabra (desktop + API)
- *Źródło: docs.palabra.ai/docs/glossaries*

### Security & Compliance

| Aspekt | Palabra |
|--------|---------|
| **Szyfrowanie** | End-to-end encryption dla wszystkich konwersacji |
| **Przechowywanie danych** | Audio usuwane po przetworzeniu, text encrypted at rest |
| **GDPR** | 100% compliant |
| **Certyfikaty** | ISO, SOC 2 (w trakcie) |

### Extensibility: Context-Aware Enhancements (spełnia Twoje wymagania)

Palabra API pozwala na programowe rozszerzenia:

1. **Dynamic glossary switching** — zmiana glossary w trakcie sesji przez API (dopasowanie do tematu rozmowy)
2. **Conversation history** — możliwość przechwytywania transkryptów (event `transcription`) do budowania kontekstu
3. **Voice cloning API** — zachowanie tożsamości głosowej mówcy
4. **Multi-target** — tłumaczenie na wiele języków jednocześnie (`addTranslationTarget()`)
5. **Session API** — dla strumieni SRT/RTMP (OBS, YouTube, vMix)

*Źródło: palabra.ai (strona produktowa), docs.palabra.ai, npm @palabra-ai/translator*

## Architectural Patterns Analysis — System oparty na Pipecat

### Architektura systemu — poziom koncepcyjny

```
┌──────────────────────────────────────────────────────────────┐
│                     Użytkownik (Teams/Meet)                    │
│         ┌─────────────┴─────────────┐                        │
│         │   Osoba A (PL)            │  Osoba B (EN)          │
│         └─────────────┬─────────────┘                        │
│                       │ audio systemowe                       │
│                       ▼                                       │
│  ┌──────────────────────────────────────────────────┐        │
│  │              Overlay / Sidecar App                 │        │
│  │  (Electron/Tauri — przezroczyste okno nad Teams)   │        │
│  └──────────────────────┬───────────────────────────┘        │
│                         │ WebSocket                           │
│                         ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                 Pipecat Pipeline                          │  │
│  │                                                           │  │
│  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐      │  │
│  │  │ VAD  │→ │ STT  │→ │ LLM  │→ │ TTS  │→ │Transport│    │  │
│  │  │Silero│  │Whisper│  │GPT-4o│  │Kokoro│  │ WebRTC  │    │  │
│  │  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘      │  │
│  │                    │                                      │  │
│  │                    ▼                                      │  │
│  │           ┌──────────────────┐                            │  │
│  │           │  Sugestia Engine  │                            │  │
│  │           │  (LLM + RAG)     │                            │  │
│  │           └──────────────────┘                            │  │
│  └─────────────────────────────────────────────────────────┘  │
│                         │                                      │
│                         ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Vector Database                              │  │
│  │  (knowledge base — zwroty, zdania, dokumenty tematyczne)  │  │
│  └─────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Pipeline Pipecat — komponenty

| Stage | Komponent Pipecat | Rekomendacja | Uzasadnienie |
|-------|------------------|-------------|--------------|
| **Transport** | `DailyTransport` / `WebSocketTransport` | Daily.co WebRTC | Globalna infrastruktura, 13ms first-hop latency |
| **VAD** | `SileroVADAnalyzer` | Silero VAD v5 | Standard branżowy, 10-50ms latency |
| **STT** | `DeepgramSTTService` / `WhisperSTTService` | **Whisper large-v3** (lokalnie) lub **Deepgram Nova-3** | PL działa w obu; Deepgram ma niższy TTFB |
| **LLM** | `OpenAILLMService` / `AnthropicLLMService` | **GPT-4o** lub **Claude 4** | Tłumaczenie + generowanie sugestii w jednym |
| **TTS** | `CartesiaTTSService` / `ElevenLabsTTSService` | **Kokoro-82M** (lokalnie) lub **Cartesia Sonic-3** | PL wspierany, <200ms TTFA |
| **RAG** | `FrameProcessor` (custom) + Vector DB | **Qdrant** lub **pgvector** | Niska latencja, skalowalność |

*Źródło: docs.pipecat.ai, BrightCoding Pipecat Guide 2026, FutureAGI Latency Optimization 2026*

### Architektura sugerowania odpowiedzi (Context-Aware Suggestions)

System sugestii działa jako **równoległy FrameProcessor** w pipeline Pipecat:

```
Przychodzący audio (osoba B mówi po angielsku)
    → Whisper STT → transkrypt EN
    → LLM (GPT-4o):
        ├─ Tłumaczenie na PL → TTS → do słuchawek osoby A
        └─ Analiza + RAG:
              ├─ Embedding ostatniego zdania
              ├─ Semantic search w Vector DB
              ├─ Generowanie sugestii
              └→ Overlay UI: "Możesz odpowiedzieć: [sugestia]"
```

**Prompt LLM dla sugestii (przykład):**
```
Jesteś asystentem polskiego użytkownika podczas rozmowy biznesowej
ze Szwajcarem. Temat: [konkretny temat].
Przetłumacz poniższy tekst na polski.
Następnie, na podstawie:
- historii rozmowy,
- przygotowanej bazy zwrotów (RAG),
- kontekstu ostatniej wypowiedzi,
zaproponuj 1-2 zdania jak odpowiedzieć po polsku.

Ostatnia wypowiedź (EN): "..."
Sugestia odpowiedzi (PL):
```

### Skalowalność i Performance

| Parametr | Cel | Jak osiągnąć |
|----------|-----|-------------|
| End-to-end latency | **<800ms** | Streaming pipeline (partial frames), VAD + STT + LLM + TTS równolegle |
| TTFA (Time to First Audio) | **<300ms** | Cartesia Sonic-3 (188ms) / Kokoro streaming |
| Barge-in (przerywanie) | <500ms | Native w Pipecat przez `InterruptionFrame` |
| Concurrent sessions | Skalowanie horyzontalne | Pipecat Cloud (Daily.co infrastructure) |
| Vector search | <50ms | Qdrant in-memory, indeks HNSW |

*Źródło: FutureAGI Pipecat Latency Optimization 2026, AssemblyAI Voice Agent Architecture*

### Security Architecture

| Aspekt | Implementacja |
|--------|--------------|
| **Audio encryption** | WebRTC SRTP/SRTCP (DTLS handshake) |
| **API keys** | Environment variables, nie w kodzie |
| **Vector DB** | Szyfrowanie at-rest, private network |
| **LLM API** | TLS, bez logowania audio |
| **GDPR** | Możliwość hostowania w EU (Daily.co EU PoP + Qdrant EU region) |

### Deployment Options

| Opcja | Zalety | Koszt |
|-------|--------|-------|
| **Pipecat Cloud** (Daily.co) | Zarządzana infra, auto-scaling, WebRTC transport | Płatny (usage-based) |
| **VPS + Docker** | Pełna kontrola, niższy koszt przy stałym użyciu | ~$50-200/mies. |
| **Local/on-prem** | Zero latency sieciowej, pełne bezpieczeństwo | Wymaga GPU (RTX 3060+) |

*Źródło: daily.co/products/pipecat-cloud, Pipecat GitHub*

## Implementation Research — Plan budowy systemu Pipecat

### Fazy implementacji

#### Faza 0: Proof of Concept (1-2 tygodnie)
**Cel:** Działający pipeline Pipecat w local environment

```
pip install pipecat-ai[deepgram,cartesia,openai]
```

- Uruchomienie `simple-chatbot` z przykładów Pipecat
- STT: Deepgram Nova-3 lub Whisper (lokalnie)
- LLM: GPT-4o-mini (test kosztów)
- TTS: Cartesia Sonic-3 lub Kokoro-82M
- Test: rozmowa PL→EN, EN→PL w konsoli

**Weryfikacja:**
- Latency <1s end-to-end
- Jakość tłumaczenia PL↔EN akceptowalna
- Pipeline streaming działa

**Zależności:** Python 3.11+, API keys (Deepgram/OpenAI/Cartesia)

#### Faza 1: Core Pipeline (2-3 tygodnie)
**Cel:** Pipeline gotowy do rzeczywistej konwersacji

| Komponent | Implementacja |
|-----------|--------------|
| **Transport** | Daily.co WebRTC (DailyTransport) |
| **VAD** | SileroVADAnalyzer z Pipecat |
| **STT** | Deepgram Nova-3 (lub Whisper large-v3 przez lokalny serwer) |
| **LLM** | GPT-4o (prompt: tłumacz + generuj sugestie) |
| **TTS** | Cartesia Sonic-3 (40+ języków, PL wspierany) |
| **RAG** | Qdrant (lokalnie lub cloud) + sentence-transformers |

**System prompt LLM (szablon):**
```
Jesteś asystentem rozmowy dwujęzycznej PL↔EN.
Twój cel:
1. Przetłumacz każdą wypowiedź na drugi język
2. Generuj sugestie odpowiedzi dla użytkownika PL na podstawie kontekstu
3. Używaj przygotowanej bazy wiedzy (RAG) dla terminów branżowych
4. Zachowuj historię konwersacji jako kontekst

Temat rozmowy: {topic}
Baza wiedzy (RAG): {retrieved_context}
```

**Weryfikacja:**
- Streaming działa (partial STT → LLM → TTS)
- Barge-in (przerywanie) działa
- Tłumaczenie PL↔EN płynne
- Sugestie wyświetlane w konsoli

#### Faza 2: Overlay UI (2-3 tygodnie)
**Cel:** Aplikacja desktopowa z przezroczystym oknem nad Teams/Meet

```
┌─────────────────────────────────────┐
│  Microsoft Teams / Google Meet       │
│  ┌───────────────────────────────┐   │
│  │                               │   │
│  │  (normalna rozmowa)           │   │
│  │                               │   │
│  └───────────────────────────────┘   │
│                                       │
│  ┌─ Overlay ──────────────────────┐  │
│  │ 💡 Sugestia odpowiedzi:         │  │
│  │ "Rozumiem Państwa stanowisko.  │  │
│  │  Proponuję następujące kroki:  │  │
│  │  [dalsza część sugestii...]"   │  │
│  │                                 │  │
│  │ [PL] 🔊 Osoba B mówi po ang... │  │
│  └─────────────────────────────────┘  │
└─────────────────────────────────────┘
```

**Technologia overlay'u:**
- **Electron** lub **Tauri** (Rust, lżejszy)
- WebSocket do Pipecat backend
- System audio capture (Stereo Mix / loopback)
- Przezroczyste, klikalne okno (click-through)

**Wymagania:**
- macOS: Audio loopback (BlackHole, Soundflower, lub Pipecat Daily SDK)
- Windows: Stereo Mix lub WASAPI loopback
- Linux: PulseAudio loopback

#### Faza 3: Vector DB + RAG (1-2 tygodnie)
**Cel:** Przygotowanie bazy wiedzy z domenowymi zwrotami

**Pipeline RAG:**
```
Dokumenty (PDF, DOCX, TXT)
    → chunkowanie (500-1000 znaków, overlap 50)
    → embedding (text-embedding-3-small lub all-MiniLM-L6-v2)
    → Qdrant (wektory + metadane)
    
Podczas rozmowy:
    → embed ostatniego zdania
    → semantic search (top-5)
    → dodaj do kontekstu LLM (RAG)
```

**Przygotowanie danych wejściowych:**
- Lista typowych zwrotów i zdań (CSV/JSON)
- Dokumentacja tematyczna rozmów
- Historia poprzednich rozmów (jeśli dostępna)
- Glosariusz branżowy PL↔EN

#### Faza 4: Produkcja i skalowanie (2-3 tygodnie)
**Cel:** Deployment na produkcję

**Opcje deploy:**
1. **Pipecat Cloud** — najszybsze, Daily.co infra (WebRTC + auto-scaling)
2. **Docker + VPS** — tańsze, manualna konfiguracja
3. **AWS ECS / GCP Cloud Run** — elastyczne, większa kontrola

**Monitoring:**
- Pipecat observability (wbudowane)
- Logi: STT latency, LLM TTFT, TTS TTFA
- Alerty: jeśli end-to-end >1.5s
- Koszty API na sesję

#### Koszty operacyjne (szacunek)

| Usługa | Model | Koszt/miesiąc (200h rozmów) |
|--------|-------|------|
| **STT** | Deepgram Nova-3 | ~$40 |
| **LLM** | GPT-4o | ~$200-400 |
| **TTS** | Cartesia Sonic-3 | ~$50 |
| **Vector DB** | Qdrant Cloud (1GB) | ~$25 |
| **Daily.co transport** | WebRTC | ~$50 |
| **Razem** | | **~$365-565/mies.** |

**Opcja lokalna (tańsza, jednorazowy koszt GPU):**
- Whisper large-v3 (lokalny STT) — $0
- Kokoro-82M (lokalny TTS, Apple Silicon) — $0
- Llama 3 70B (lokalny LLM) — wymaga GPU (A100 ~$1-2/h)
- Qdrant lokalny — $0
- **Koszt: głównie prąd + GPU (~$200-400/mies.)**

#### Timeline (łącznie)

| Faza | Czas | Zależności |
|------|------|-----------|
| **Faza 0:** PoC | Tydzień 1-2 | Python, klucze API |
| **Faza 1:** Core Pipeline | Tydzień 2-4 | Faza 0 ✅ |
| **Faza 2:** Overlay UI | Tydzień 4-7 | Faza 1 ✅ |
| **Faza 3:** RAG + Vector DB | Tydzień 7-9 | Faza 1 ✅, przygotowane dane |
| **Faza 4:** Produkcja | Tydzień 9-11 | Fazy 0-3 ✅ |

**Razem: ~11 tygodni do produkcyjnego MVP**

#### Wymagane umiejętności

| Obszar | Umiejętności |
|--------|-------------|
| **Python** | asyncio, WebSocket, audio processing |
| **Pipecat** | Pipeline, FrameProcessor, transporty |
| **LLM** | Prompt engineering, RAG patterns |
| **Vector DB** | Qdrant/pgvector, embeddingi |
| **Desktop** | Electron/Tauri, system audio capture |
| **DevOps** | Docker, cloud deployment (opcjonalnie) |

### Open-Source S2S Pipelines / Frameworks

**1. Hugging Face Speech-to-Speech**
- Architektura: VAD (Silero) → STT (Whisper/Parakeet) → LLM (dowolny HF) → TTS (ChatTTS/Kokoro/Qwen3-TTS)
- W pełni modułowy, każdy komponent wymienny
- Wsparcie Whisper large-v3 = PL działa
- Możliwość podmiany TTS na Kokoro-82M (wspiera PL)
- Apache 2.0
- GitHub: huggingface/speech-to-speech

**2. RealtimeSTT + RealtimeTTS (KoljaB)**
- Python library, MIT license
- STT: faster-whisper, wspiera PL
- TTS: wiele engineów, w tym systemowe
- VAD, wake words, streaming
- 9.9k stars (STT), 3.9k stars (TTS)
- Gotowy do integracji, server/client/WebSocket modes

**3. ESPnet (End-to-End Speech Processing)**
- Framework akademicki, wspiera S2T (speech-to-text translation)
- Dobre dla PL (warsztaty badawcze)
- Bardziej research-oriented
- GitHub: espnet/espnet

**4. NeMo (NVIDIA)**
- STT, TTS, NLU w jednym frameworku
- Parakeet, Canary modele
- Enterprise-ready, NVIDIA wsparcie
- Apache 2.0

### Komercyjne / API S2S Rozwiązania

| Produkt | Typ | PL? | Latency | Cena | Rozszerzalność |
|---------|-----|-----|---------|------|----------------|
| **OpenAI gpt-realtime-translate** | API (WebSocket) | Tak | ~0.8s | Pay-per-token (~$0.30/min) | Ograniczona (black box) |
| **DeepL Voice-to-Voice** | API | Tak (DeepL ma PL) | <1s | Subskrypcja enterprise | Ograniczona |
| **Palabra.ai** | API + SDK | **Tak** (ASR+TRANSL) | <1s | Kredytowy | **Słownik/glossary, voice cloning** |
| **Pinch** | WebSocket API | Ograniczony | Niska | Per-minute | Proste API |
| **Interprefy Agent** | SaaS (meetings) | Tak (80+ języków) | Niska | Enterprise | Brak API |
| **Sanas** | Enterprise SDK | 13 języków (brak PL) | Niska | Enterprise | SDK |
| **Deepgram (Nova-3 + Aura-2)** | API | Tak (50+ języków) | Niska | Per-hour | Custom models |
| **ElevenLabs** | API | Tak (32 języki, w tym PL) | ~300ms | Subskrypcja | Voice cloning, agent SDK |

*Źródło: Inworld.ai S2S Comparison 2026, Stream.io Blog*

### Integration Frameworks

| Framework | Typ | Open Source | Features |
|-----------|-----|-------------|----------|
| **Pipecat** (Daily.co) | Voice agent framework | **Tak** (v1.0.0, Apr 2026) | Vendor-agnostic, wiele modeli STT/TTS/LLM |
| **LiveKit Agents** | Voice agent platform | **Tak** (v1.5.6) | Adaptive interruption handling, dynamic endpointing |
| **FastRTC** | Python streaming audio | **Tak** | Lekki, Python-native |
| **Layercode** | Edge voice platform | Częściowo | CLI, Next.js integration, edge deployment |
| **SLNG** | Execution layer | Nie | Multi-provider routing, cost optimization |

### Kluczowe Trendy Technologiczne

1. **Native audio modele** (gpt-realtime-translate, Moshi, Step-Audio) — eliminują kaskadową architekturę, redukując latencję do 200-500ms vs 800ms-2s+ dla pipeline'ów
2. **Concurrent pipelines** — nowoczesne systemy uruchamiają STT, LLM i TTS równolegle zamiast sekwencyjnie (Gladia, 2025)
3. **Koniec DeepSpeech** (Mozilla, czerwiec 2025) — migracja na Whisper/Parakeet/Moonshine
4. **Modele edge** (Moonshine, Kokoro-82M) — umożliwiają inferencję na urządzeniu, redukując zależność od chmury
5. **Konwergencja TTS/STT** — platformy typu Gradium, Deepgram oferują obie usługi w jednym API

---

## Executive Summary

**Cel:** Wybór i zaplanowanie systemu real-time speech-to-speech do komunikacji PL↔EN z rozszerzeniem o kontekstowe sugestie odpowiedzi.

**Kluczowe wnioski:**

1. **Palabra.ai** — najlepsze gotowe rozwiązanie z glossary i wsparciem PL, ale ograniczona rozszerzalność
2. **Pipecat** — rekomendowany framework open-source do budowy własnego systemu z pełną kontrolą
3. **System hybrydowy** — jeden LLM (GPT-4o) robi tłumaczenie + generowanie sugestii + RAG
4. **Time-to-market:** ~11 tygodni do produkcyjnego MVP
5. **Koszt operacyjny:** ~$365-565/mies. (API cloud) lub ~$200-400/mies. (lokalnie z GPU)

**Rekomendacja:** Budowa systemu na Pipecat z Whisper/Deepgram (STT) + GPT-4o (LLM) + Cartesia/Kokoro (TTS) + Qdrant (vector DB). Overlay w Electron/Tauri nad Teams/Meet.

## Spis treści

1. Wprowadzenie i metodologia
2. Analiza rynku S2S — open source i komercyjne
3. Technology Stack Analysis — STT, TTS, LLM, frameworki
4. Integration Patterns — Palabra.ai (gotowe rozwiązanie)
5. Architectural Patterns — System oparty na Pipecat
6. Implementation Research — Plan budowy
7. Podsumowanie i rekomendacje

## 1. Wprowadzenie i metodologia

### Cel badawczy

Wybór optymalnego systemu real-time speech-to-speech do dwujęzycznej komunikacji PL↔EN z możliwością generowania kontekstowych sugestii odpowiedzi na podstawie przygotowanej bazy wiedzy (RAG).

### Zakres

- Rozwiązania open-source i komercyjne (API)
- Języki: polski (native) ↔ angielski (B1+)
- Wymóg: możliwość rozszerzenia o context-aware suggestions
- Platforma docelowa: Microsoft Teams / Google Meet

### Metodologia

- Web search z weryfikacją źródłową (Q1-Q2 2026)
- Multi-source validation dla kluczowych claimów
- Benchmarki i dane porównawcze z niezależnych źródeł

## 2. Analiza rynku S2S

### Gotowe rozwiązania z wsparciem PL

| Rozwiązanie | Typ | PL | Glossary | API | Cena |
|------------|-----|----|----------|-----|------|
| **Palabra.ai** | API + Desktop | ✅ ASR+TRANSL | ✅ CSV | ✅ Python/JS/Java | Kredytowy |
| **OpenAI gpt-realtime-translate** | API | ✅ (model) | ❌ | ✅ WebSocket | ~$0.30/min |
| **DeepL Voice-to-Voice** | API | ✅ | ❌ (na ten moment) | ✅ | Enterprise |
| **ElevenLabs** | API | ✅ TTS | ❌ | ✅ | Subskrypcja |
| **Interprefy Agent** | SaaS | ✅ 80+ języków | ❌ | ❌ | Enterprise |
| **Pinch** | API | Ograniczony | ❌ | ✅ WebSocket | Per-minute |

### Frameworki open-source do budowy własnego systemu

| Framework | Open Source | PL | RAG | Overlay |
|-----------|-------------|-----|-----|---------|
| **Pipecat** | ✅ BSD-2 (v1.0.0) | ✅ przez STT/TTS | ✅ FrameProcessor | ❌ (do zbudowania) |
| **LiveKit Agents** | ✅ Apache (v1.5.6) | ✅ przez STT/TTS | ❌ (custom) | ❌ |
| **Hugging Face S2S** | ✅ Apache 2.0 | ✅ (Whisper+ Kokoro) | ❌ | ❌ |
| **RealtimeSTT/TTS** | ✅ MIT | ✅ (Whisper) | ❌ | ❌ |

## 6. — Plan implementacji

### Fazy

| Faza | Czas | Opis |
|------|------|------|
| **Faza 0:** PoC | 1-2 tyg. | Pipeline Pipecat w konsoli (STT→LLM→TTS) |
| **Faza 1:** Core Pipeline | 2-3 tyg. | Daily transport, streaming, barge-in, sugestie |
| **Faza 2:** Overlay UI | 2-3 tyg. | Electron/Tauri nakładka nad Teams/Meet |
| **Faza 3:** RAG + Vector DB | 1-2 tyg. | Qdrant, embeddingi, przygotowanie danych |
| **Faza 4:** Produkcja | 2-3 tyg. | Deployment, monitoring, skalowanie |
| **Razem** | **~11 tyg.** | **Do produkcyjnego MVP** |

### Stack rekomendowany

| Komponent | Wybór | Alternatywa |
|-----------|-------|-------------|
| Framework | **Pipecat** (v1.0.0) | LiveKit Agents |
| Transport | **Daily.co WebRTC** | WebSocket własny |
| VAD | **Silero VAD v5** | — |
| STT | **Deepgram Nova-3** (cloud) lub **Whisper large-v3** (lokalnie) | Qwen3-ASR |
| LLM | **GPT-4o** | Claude 4 Opus |
| TTS | **Cartesia Sonic-3** (cloud) lub **Kokoro-82M** (lokalnie) | ElevenLabs |
| Vector DB | **Qdrant** | pgvector, Pinecone |
| Embedding | **text-embedding-3-small** | all-MiniLM-L6-v2 |
| Overlay | **Tauri** (Rust, lżejszy) | Electron |

### Koszty (200h rozmów/mies.)

| Scenariusz | Koszt/mies. |
|-----------|-------------|
| **Cloud API** (Deepgram+GPT-4o+Cartesia+Qdrant+Daily) | ~$365-565 |
| **Lokalnie** (Whisper+Kokoro+Llama 3 70B+Qdrant) | ~$200-400 (GPU) |
| **Hybryda** (Whisper lokalnie + GPT-4o API + Kokoro lokalnie) | ~$200-300 |

## 7. Podsumowanie i rekomendacje

### Rekomendacja końcowa

**Pipecat + Deepgram/Whisper + GPT-4o + Cartesia/Kokoro + Qdrant**

| Kryterium | Ocena |
|-----------|-------|
| Jakość tłumaczenia PL↔EN | ⭐⭐⭐⭐⭐ (GPT-4o + Whisper large-v3) |
| Latency | ~500-800ms (streaming pipeline) |
| Sugestie kontekstowe | ✅ RAG + Vector DB |
| Glossary branżowy | ✅ Prompt + RAG |
| Łatwość startu | ⭐⭐ (wymaga budowy) |
| Koszt operacyjny | ⭐⭐⭐ (~$300-500/mies.) |
| Skalowalność | ⭐⭐⭐⭐⭐ (Daily.co infrastructure) |
| Bezpieczeństwo | ⭐⭐⭐⭐⭐ (WebRTC SRTP, GDPR EU) |

### Następne kroki

1. **Tydzień 1:** Instalacja Pipecat, test example chatbot, weryfikacja PL↔EN
2. **Tydzień 2:** Konfiguracja Daily transport, test WebRTC
3. **Tydzień 3:** Implementacja system prompt LLM (tłumacz + sugestie)
4. **Tydzień 4:** Overlay UI — prototyp Electron/Tauri
5. **Tydzień 5+:** RAG + Vector DB + production hardening

---

**Data zakończenia:** 2026-06-13
**Weryfikacja źródeł:** Wszystkie fakty techniczne zweryfikowane z aktualnymi źródłami webowymi
**Poziom ufności:** Wysoki — oparty na wielu autorytatywnych źródłach
