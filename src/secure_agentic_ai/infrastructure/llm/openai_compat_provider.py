import httpx


class OpenAICompatibleChatProvider:
    def __init__(
        self,
        api_key: str,
        *,
        provider_name: str,
        model: str,
        base_url: str,
        timeout_s: float = 60.0,
    ) -> None:
        self._api_key = api_key
        self._provider_name = provider_name
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout_s = timeout_s

    @property
    def label(self) -> str:
        return f"{self._provider_name}:{self._model}"

    def is_available(self) -> bool:
        return bool(self._api_key)

    async def complete(self, messages: list[dict[str, str]]) -> str:
        if not self._api_key:
            raise RuntimeError(f"{self._provider_name} API key is not configured")

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
            raise RuntimeError(f"{self._provider_name} returned no choices")
        message = choices[0].get("message", {})
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError(f"{self._provider_name} returned empty content")
        return content.strip()
