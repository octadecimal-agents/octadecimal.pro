import re

AO_SYSTEM_PROMPT = """Jesteś Agentem Osobistym CEO Octadecimal (Maja — planowanie, Anna — ton).
Odpowiadaj po polsku, zwięźle, w Markdown.
Korzystaj wyłącznie z podanego kontekstu Knowledge — nie zgaduj.
Gdy brakuje danych, powiedz to wprost.
Na końcu dodaj jedną linię z sugestią panelu: → `#Planning`, `#Board`, `#Wiki` lub `#Review`."""

# MiniMax-M3 may embed chain-of-thought in XML-like blocks before the user-facing answer.
_THINK_TAG = "think"
_LLM_REASONING_RE = re.compile(
    rf"(?:<think>.*?</think>|<{_THINK_TAG}>.*?</{_THINK_TAG}>)\s*",
    re.DOTALL | re.IGNORECASE,
)


def sanitize_llm_reply(text: str) -> str:
    """Strip MiniMax reasoning blocks from user-visible chat output."""
    return _LLM_REASONING_RE.sub("", text).strip()


def build_rag_messages(user_message: str, context_blocks: list[tuple[str, str]]) -> list[dict[str, str]]:
    context = "\n\n".join(f"### {source}\n{excerpt}" for source, excerpt in context_blocks if excerpt.strip())
    user_content = user_message
    if context:
        user_content = f"Kontekst Knowledge:\n\n{context}\n\n---\n\nPytanie CEO: {user_message}"
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
