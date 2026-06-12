<link rel="stylesheet" href="../styles/main.css">

# Faza 1: Python Platform Foundation

[← Indeks planowania](README.md) | [Roadmapa](roadmap-draft.md) | [Python](../technologies/Python.md) | [uv](../technologies/uv.md) | [Pytest](../technologies/Pytest.md) | [Ruff](../technologies/Ruff.md) | [Mypy](../technologies/Mypy.md)

Status: prywatna instrukcja robocza

Cel fazy: zbudować minimalny, profesjonalny fundament projektu Python, wykonując kroki ręcznie i świadomie, tak aby zrozumieć strukturę projektu, tooling, testy, typowanie i podstawowy workflow developerski.

W tej fazie rezygnujemy ze środowiska M1 jako aktywnego elementu architektury. Pracujemy lokalnie w repo projektu i budujemy docelowy fundament pod aplikację Python/FastAPI.

## Zasada pracy

Nie chodzi o szybkie wygenerowanie plików. Chodzi o nauczenie się:

- jak wygląda nowoczesny projekt Python,
- czym jest `pyproject.toml`,
- jak działa `uv`,
- jak projektować strukturę pakietu,
- jak uruchamiać testy,
- jak używać `ruff`,
- jak używać `mypy`,
- jak przygotować CI,
- jak każdy commit ma wzmacniać portfolio.

Każdy punkt wykonuj ręcznie. Jeśli utkniesz, podaj numer kroku i output terminala.

## Oczekiwany efekt końcowy

Po zakończeniu fazy powinno działać:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy .
```

Repo powinno mieć minimalną strukturę:

```text
src/secure_agentic_ai/
├── __init__.py
├── domain/
│   └── __init__.py
├── application/
│   └── __init__.py
├── adapters/
│   └── __init__.py
└── infrastructure/
    └── __init__.py

tests/
├── unit/
│   └── test_package_import.py
├── integration/
└── evals/
```

## Checklist

### 1. Sprawdź czystość repo

Status: [x]

Komenda:

```bash
git status --short --branch
```

Cel:

Upewnić się, że publiczne repo nie ma przypadkowych zmian przed rozpoczęciem fazy.

Oczekiwane:

```text
## main...origin/main
```

Ignorowane `.dev/`, `.history/` i `.DS_Store` mogą istnieć, ale nie powinny być publicznymi zmianami.

Jeśli widzisz `??` albo `M`, zatrzymaj się i sprawdź, co to jest.

### 2. Sprawdź wersję Pythona

Status: [x]

Komendy:

```bash
python3 --version
which python3
```

Cel:

Zobaczyć, jakiego Pythona uruchamia system i skąd pochodzi.

Do zapamiętania:

- `python3 --version` pokazuje wersję interpretera.
- `which python3` pokazuje ścieżkę do wykonywanego programu.

Oczekiwane:

Python 3.12 albo 3.13. Jeśli masz starszą wersję, nie naprawiaj na ślepo — zatrzymaj się i poproś o pomoc.

### 3. Sprawdź, czy jest `uv`

Status: [x]

Komenda:

```bash
uv --version
```

Cel:

Sprawdzić, czy masz zainstalowany nowoczesny manager środowiska i zależności dla Pythona.

Jeśli `uv` nie istnieje, zatrzymaj się. Najpierw omówimy instalację, żeby nie mieszać narzędzi.

### 4. Utwórz branch dla fazy

Status: [x]

Komenda:

```bash
git switch -c feature/python-platform-foundation
```

Cel:

Nie pracować bezpośrednio na `main`. To jest dobry nawyk zawodowy.

Do zapamiętania:

- `git switch` przełącza gałąź.
- `-c` tworzy nową gałąź.
- nazwa brancha mówi, jaki jest zakres pracy.

### 5. Zainicjalizuj projekt Python

Status: [x]

Komenda:

```bash
uv init --package --name secure-agentic-ai-platform
```

Cel:

Utworzyć `pyproject.toml` i podstawową strukturę projektu.

Uwaga:

Jeśli `uv` proponuje utworzenie dodatkowych plików, nie panikuj. Po komendzie sprawdź:

```bash
find . -maxdepth 3 -type f | sort
```

Nie commituj jeszcze.

### 6. Obejrzyj `pyproject.toml`

Status: [x]

Komenda:

```bash
sed -n '1,220p' pyproject.toml
```

Cel:

Zrozumieć, że `pyproject.toml` jest centralnym plikiem konfiguracji projektu Python.

Zwróć uwagę na:

- `[project]`,
- `name`,
- `version`,
- `requires-python`,
- `dependencies`,
- `[build-system]`.

Pytanie kontrolne:

Czy chcesz, żebym wyjaśnił dokładnie składnię TOML i sekcje `pyproject.toml`?

### 7. Ustaw docelową wersję Pythona

Status: [x]

Cel:

Upewnić się, że projekt wymaga nowoczesnego Pythona.

Docelowo w `pyproject.toml` chcemy:

```toml
requires-python = ">=3.12"
```

Jeśli `uv init` ustawi coś innego, zapisz to i poproś o pomoc przed edycją.

### 8. Dodaj zależności developerskie

Status: [x]

Komenda:

```bash
uv add --dev pytest ruff mypy
```

Cel:

Dodać narzędzia jakości kodu.

Co oznacza:

- `uv add` dodaje zależność.
- `--dev` oznacza zależność developerską, nie runtime.
- `pytest` uruchamia testy.
- `ruff` lintuje i formatuje kod.
- `mypy` sprawdza typy statycznie.

Po komendzie sprawdź:

```bash
sed -n '1,260p' pyproject.toml
```

### 9. Utwórz strukturę pakietu

Status: [x]

Komendy:

```bash
mkdir -p src/secure_agentic_ai/domain
mkdir -p src/secure_agentic_ai/application
mkdir -p src/secure_agentic_ai/adapters
mkdir -p src/secure_agentic_ai/infrastructure
touch src/secure_agentic_ai/__init__.py
touch src/secure_agentic_ai/domain/__init__.py
touch src/secure_agentic_ai/application/__init__.py
touch src/secure_agentic_ai/adapters/__init__.py
touch src/secure_agentic_ai/infrastructure/__init__.py
```

Cel:

Utworzyć strukturę pod Clean Architecture.

Do zapamiętania:

- `mkdir -p` tworzy katalogi pośrednie i nie zgłasza błędu, jeśli katalog już istnieje.
- `touch` tworzy pusty plik albo aktualizuje timestamp istniejącego.
- `__init__.py` oznacza pakiet Pythona.

Pytanie kontrolne:

Czy chcesz pogłębić temat pakietów, modułów i importów w Pythonie?

### 10. Utwórz strukturę testów

Status: [x]

Komendy:

```bash
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/evals
```

Cel:

Od początku rozdzielać typy testów.

Znaczenie:

- `unit` — szybkie testy logiki bez infrastruktury,
- `integration` — testy z bazą/API/zewnętrznymi adapterami,
- `evals` — testy zachowania LLM/RAG/agentów.

### 11. Dodaj pierwszy test importu

Status: [x]

Utwórz plik:

```text
tests/unit/test_package_import.py
```

Treść:

```python
import secure_agentic_ai


def test_package_imports() -> None:
    assert secure_agentic_ai is not None
```

Cel:

Sprawdzić, czy pakiet instaluje się i importuje poprawnie.

To jest mały test, ale bardzo dobry na start: wykrywa problemy ze strukturą `src/`.

### 12. Uruchom testy

Status: [x]

Komenda:

```bash
uv run pytest
```

Cel:

Uruchomić testy w środowisku zarządzanym przez `uv`.

Do zapamiętania:

- `uv run` wykonuje komendę w kontekście projektu.
- `pytest` automatycznie znajduje pliki `test_*.py`.

Oczekiwane:

Jeden test przechodzi.

### 13. Dodaj konfigurację Ruff

Status: [x]

W `pyproject.toml` docelowo dodajemy:

```toml
[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
```

Cel:

Ustawić jasne reguły jakości kodu.

Nie edytuj na ślepo, jeśli nie czujesz się pewnie w TOML. Poproś o pomoc, a przejdziemy przez to linia po linii.

### 14. Uruchom Ruff lint

Status: [x]

Komenda:

```bash
uv run ruff check .
```

Cel:

Sprawdzić kod pod kątem błędów, importów i prostych problemów jakości.

Jeśli pojawią się błędy, nie poprawiaj ich losowo. Wklej output.

### 15. Uruchom Ruff format check

Status: [x]

Komenda:

```bash
uv run ruff format --check .
```

Cel:

Sprawdzić formatowanie bez zmieniania plików.

Jeśli format check failuje, użyj:

```bash
uv run ruff format .
```

a potem powtórz:

```bash
uv run ruff format --check .
```

### 16. Dodaj konfigurację mypy

Status: [x]

W `pyproject.toml` docelowo dodajemy:

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
```

Cel:

Od początku ustawić typowanie jako element jakości.

Uwaga:

`strict = true` może być wymagające. To dobrze dla nauki, ale jeśli zablokuje nas zbyt wcześnie, możemy świadomie poluzować ustawienia.

### 17. Uruchom mypy

Status: [x]

Komenda:

```bash
uv run mypy .
```

Cel:

Sprawdzić typy w projekcie.

Jeśli mypy zgłosi problem z importem pakietu albo konfiguracją, zatrzymaj się i wklej output.

### 18. Dodaj minimalny README update

Status: [x]

Cel:

Dodać do publicznego README krótką sekcję `Development`, ale dopiero gdy komendy faktycznie działają.

Docelowa treść będzie zawierała:

```markdown
## Development

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy .
```
```

Nie rób tego przed weryfikacją komend.

### 19. Dodaj GitHub Actions

Status: [ ]

Utwórz:

```text
.github/workflows/python-quality.yml
```

Cel:

Automatycznie uruchamiać testy i quality gates na GitHubie.

Minimalny workflow dodamy dopiero po lokalnym przejściu:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy .
```

### 20. Sprawdź pełny stan przed commitem

Status: [ ]

Komendy:

```bash
git status --short
git diff --stat
```

Cel:

Zobaczyć dokładnie, co trafi do commita.

Oczekiwane typy zmian:

- `pyproject.toml`,
- `uv.lock`,
- `src/...`,
- `tests/...`,
- `.github/workflows/python-quality.yml`,
- `README.md`.

Nie powinno wejść:

- `.dev/`,
- `.history/`,
- `.DS_Store`,
- prywatne notatki,
- lokalne logi,
- stare `docs/install` z macOS runtime.

### 21. Commit 1: tooling

Status: [ ]

Proponowany commit:

```bash
git add pyproject.toml uv.lock src tests
git commit -m "chore(python): initialize project tooling"
```

Uwaga:

Zakres commita ustalimy dokładnie po obejrzeniu `git status`. Nie commituj bez finalnego sprawdzenia.

### 22. Commit 2: CI i README

Status: [ ]

Proponowany commit:

```bash
git add README.md .github/workflows/python-quality.yml
git commit -m "chore(ci): add Python quality workflow"
```

Uwaga:

Może się okazać, że lepiej zrobić jeden commit albo inny podział. Zdecydujemy po stanie plików.

### 23. Push brancha

Status: [ ]

Komenda:

```bash
git push -u origin feature/python-platform-foundation
```

Cel:

Wypchnąć branch, ale nie merge'ować od razu do `main`.

### 24. Review fazy

Status: [ ]

Po pushu robimy krótkie review:

- czy komendy lokalnie działają,
- czy CI działa,
- czy README jest zgodne z rzeczywistością,
- czy historia commitów wygląda profesjonalnie,
- czego się nauczyłeś,
- co wymaga pogłębienia.

## Notatki wiedzy do uzupełnienia

W trakcie fazy warto dopisać prywatne notatki do:

- `.dev/technologies/Python.md`,
- `.dev/technologies/uv.md`,
- `.dev/technologies/Pytest.md`,
- `.dev/technologies/Ruff.md`,
- `.dev/technologies/Mypy.md`,
- `.dev/technologies/CleanArchitecture.md`.

## Pytania kontrolne dla rozmowy rekrutacyjnej

Po tej fazie powinieneś umieć odpowiedzieć:

1. Dlaczego używasz `src/` layout?
2. Po co jest `pyproject.toml`?
3. Czym różnią się zależności runtime od dev dependencies?
4. Dlaczego `ruff`, `mypy` i `pytest` są częścią quality gate?
5. Co daje `uv run`?
6. Dlaczego zaczynamy od testów, zanim dodamy AI workflow?
7. Jak ta faza wspiera późniejsze FastAPI/LangGraph/RAG?

## Decyzje odłożone

Na tym etapie nie decydujemy jeszcze:

- czy Qdrant czy pgvector będzie pierwszym backendem retrieval,
- jak dokładnie będzie wyglądał LangGraph workflow,
- czy UI będzie w React/Next.js czy prostsze,
- jak będzie wyglądał Bitwarden adapter,
- czy macOS local runtime wróci jako publiczne case study.
