import re

AO_SYSTEM_PROMPT = """Jesteś Agentem Osobistym CEO Octadecimal — łączysz głos Maji (struktura, plan, konkret)
i Anny (ciepły, rzeczowy ton). Odpowiadaj po polsku, krótko, w Markdown.

Zasady:
1. Korzystaj wyłącznie z podanego kontekstu (Knowledge, tablica, review, plan) — nie zgaduj.
2. Przy braku danych powiedz to wprost i zaproponuj `#Wiki` albo właściwy panel.
3. Cytuj Kanon ścieżką pliku (np. `01-Base-Point/.../Backup.md`), nie wymyślonym tytułem.
4. Nigdy nie wymyślaj liczby akcji HITL ani listy approval — to zawsze pochodzi z narzędzi.
5. Zawsze kończ jedną linią z sugestią panelu: → `#Planning`, `#Board`, `#Wiki` lub `#Review`."""

# MiniMax-M3 may embed chain-of-thought in XML-like blocks before the user-facing answer.
_THINK_TAG = "think"
_LLM_REASONING_RE = re.compile(
    rf"(?:<think>.*?</think>|<{_THINK_TAG}>.*?</{_THINK_TAG}>)\s*",
    re.DOTALL | re.IGNORECASE,
)


def sanitize_llm_reply(text: str) -> str:
    """Strip MiniMax reasoning blocks from user-visible chat output."""
    return _LLM_REASONING_RE.sub("", text).strip()


def build_rag_messages(
    user_message: str,
    context_blocks: list[tuple[str, str]],
    *,
    tool_summaries: list[str] | None = None,
) -> list[dict[str, str]]:
    sections: list[str] = []
    if tool_summaries:
        sections.append("Wyniki narzędzi:\n\n" + "\n\n".join(tool_summaries))
    context = "\n\n".join(f"### {source}\n{excerpt}" for source, excerpt in context_blocks if excerpt.strip())
    if context:
        sections.append("Fragmenty Knowledge:\n\n" + context)
    user_content = user_message
    if sections:
        user_content = "\n\n---\n\n".join(sections) + f"\n\n---\n\nPytanie CEO: {user_message}"
    return [
        {"role": "system", "content": AO_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


def parse_suggested_hash(text: str) -> str | None:
    lowered = text.lower()
    for needle, tag in {
        "#review": "#Review",
        "#board": "#Board",
        "#planning": "#Planning",
        "#wiki": "#Wiki",
    }.items():
        if needle in lowered:
            return tag
    if "→ `#" in text:
        fragment = text.split("→ `#", 1)[1]
        name = fragment.split("`", 1)[0].strip()
        if name:
            return f"#{name}"
    return None
