from secure_agentic_ai.application.ports import ChatCompletionProvider
from secure_agentic_ai.infrastructure.llm.deepseek_provider import DeepSeekChatProvider, DryChatProvider
from secure_agentic_ai.infrastructure.llm.secret_resolver import resolve_deepseek_api_key
from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig


async def build_chat_provider(config: WorkspaceConfig) -> ChatCompletionProvider:
    if config.llm_provider == "deepseek":
        api_key = await resolve_deepseek_api_key(
            knowledge_root=config.knowledge_root,
            bw_label=config.deepseek_bw_label,
        )
        if api_key:
            return DeepSeekChatProvider(
                api_key,
                model=config.deepseek_model,
                base_url=config.deepseek_base_url,
            )
    return DryChatProvider()
