from dataclasses import dataclass

from secure_agentic_ai.application.ports import ChatCompletionProvider
from secure_agentic_ai.infrastructure.llm.deepseek_provider import DeepSeekChatProvider, DryChatProvider
from secure_agentic_ai.infrastructure.llm.minimax_provider import MiniMaxChatProvider
from secure_agentic_ai.infrastructure.llm.secret_resolver import (
    resolve_deepseek_api_key,
    resolve_minimax_api_token,
)
from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig


@dataclass(frozen=True)
class ResolvedChatProvider:
    provider: ChatCompletionProvider
    requested: str
    active: str
    fallback_reason: str | None = None


async def resolve_chat_provider(config: WorkspaceConfig) -> ResolvedChatProvider:
    requested = config.llm_provider
    if requested == "minimax":
        api_token = await resolve_minimax_api_token(
            knowledge_root=config.knowledge_root,
            bw_label=config.minimax_bw_label,
        )
        if api_token:
            return ResolvedChatProvider(
                provider=MiniMaxChatProvider(
                    api_token,
                    model=config.minimax_model,
                    base_url=config.minimax_base_url,
                ),
                requested=requested,
                active="minimax",
            )
        return ResolvedChatProvider(
            provider=DryChatProvider(),
            requested=requested,
            active="dry",
            fallback_reason="Brak MINIMAX_API_TOKEN — odpowiedzi oparte na RAG i heurystykach.",
        )

    if requested == "deepseek":
        api_key = await resolve_deepseek_api_key(
            knowledge_root=config.knowledge_root,
            bw_label=config.deepseek_bw_label,
        )
        if api_key:
            return ResolvedChatProvider(
                provider=DeepSeekChatProvider(
                    api_key,
                    model=config.deepseek_model,
                    base_url=config.deepseek_base_url,
                ),
                requested=requested,
                active="deepseek",
            )
        return ResolvedChatProvider(
            provider=DryChatProvider(),
            requested=requested,
            active="dry",
            fallback_reason="Brak DEEPSEEK_API_KEY — odpowiedzi oparte na RAG i heurystykach.",
        )

    return ResolvedChatProvider(
        provider=DryChatProvider(),
        requested=requested,
        active="dry",
    )


async def build_chat_provider(config: WorkspaceConfig) -> ChatCompletionProvider:
    return (await resolve_chat_provider(config)).provider
