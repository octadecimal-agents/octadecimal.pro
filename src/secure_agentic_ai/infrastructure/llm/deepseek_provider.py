import httpx

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-flash"

AO_SYSTEM_PROMPT = """Jesteś Agentem Osobistym CEO Octadecimal (Maja — planowanie, Anna — ton).
Odpowiadaj po polsku, zwięźle, w Markdown.
Korzystaj wyłącznie z podanego kontekstu Knowledge — nie zgaduj.
Gdy brakuje danych, powiedz to wprost.
Na końcu dodaj jedną linię z sugestią panelu: → `#Planning`, `#Board`, `#Wiki` lub `#Review`."""


class DeepSeekChatProvider:
    def __init__(
        self,
        api_key: str,
        *,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        timeout_s: float = 60.0,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout_s = timeout_s

    @property
    def label(self) -> str:
        return f"deepseek:{self._model}"

    def is_available(self) -> bool:
        return bool(self._api_key)

    async def complete(self, messages: list[dict[str, str]]) -> str:
        if not self._api_key:
            raise RuntimeError("DeepSeek API key is not configured")

        payload = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "temperature": 0.4,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=self._timeout_s) as client:
            response = await client.post(
                f"{self._base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            raise RuntimeError("DeepSeek returned no choices")
        message = choices[0].get("message", {})
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("DeepSeek returned empty content")
        return content.strip()


class DryChatProvider:
    @property
    def label(self) -> str:
        return "dry"

    def is_available(self) -> bool:
        return False

    async def complete(self, messages: list[dict[str, str]]) -> str:
        raise RuntimeError("DryChatProvider does not call external LLM")


def build_rag_messages(user_message: str, context_blocks: list[tuple[str, str]]) -> list[dict[str, str]]:
    context = "\n\n".join(
        f"### {source}\n{excerpt}" for source, excerpt in context_blocks if excerpt.strip()
    )
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
