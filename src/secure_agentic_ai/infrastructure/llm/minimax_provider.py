from secure_agentic_ai.infrastructure.llm.openai_compat_provider import OpenAICompatibleChatProvider

DEFAULT_BASE_URL = "https://api.minimax.io/v1"
DEFAULT_MODEL = "MiniMax-M3"


class MiniMaxChatProvider(OpenAICompatibleChatProvider):
    def __init__(
        self,
        api_key: str,
        *,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        timeout_s: float = 60.0,
    ) -> None:
        super().__init__(
            api_key,
            provider_name="minimax",
            model=model,
            base_url=base_url,
            timeout_s=timeout_s,
        )
