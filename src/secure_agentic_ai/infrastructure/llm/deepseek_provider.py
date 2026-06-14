from secure_agentic_ai.infrastructure.llm.chat_prompts import (
    AO_SYSTEM_PROMPT,
    build_rag_messages,
    parse_suggested_hash,
)
from secure_agentic_ai.infrastructure.llm.openai_compat_provider import OpenAICompatibleChatProvider

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-flash"

__all__ = [
    "AO_SYSTEM_PROMPT",
    "DEFAULT_BASE_URL",
    "DEFAULT_MODEL",
    "DeepSeekChatProvider",
    "DryChatProvider",
    "build_rag_messages",
    "parse_suggested_hash",
]


class DeepSeekChatProvider(OpenAICompatibleChatProvider):
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
            provider_name="deepseek",
            model=model,
            base_url=base_url,
            timeout_s=timeout_s,
        )


class DryChatProvider:
    @property
    def label(self) -> str:
        return "dry"

    def is_available(self) -> bool:
        return False

    async def complete(self, messages: list[dict[str, str]]) -> str:
        raise RuntimeError("DryChatProvider does not call external LLM")
