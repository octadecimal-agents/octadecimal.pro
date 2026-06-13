from uuid import uuid4

from secure_agentic_ai.application.commands import RequestActionCommand
from secure_agentic_ai.application.use_cases import RequestActionStatus, RequestActionUseCase
from secure_agentic_ai.domain.actors import Actor, ActorType
from secure_agentic_ai.domain.policies import Action, ActionType, RiskLevel

_DOCUMENTS: dict[str, str] = {
    "governance-overview": (
        "The secure agentic AI platform provides governance for autonomous agents. "
        "Every action must pass through a policy evaluation before execution. "
        "Human approval is required for high-risk actions such as writing files or resolving secrets."
    ),
    "policy-rules": (
        "Policy evaluation checks the actor type and risk level of each action. "
        "Low-risk actions by human actors are allowed automatically. "
        "High-risk actions by agents always require human-in-the-loop approval."
    ),
    "audit-trail": (
        "The audit trail records every policy decision and action execution. "
        "Each audit event includes an event type, actor identifier, action type, and timestamp. "
        "Audit events are immutable and stored in the persistence layer."
    ),
}


class ToolExecutionError(Exception):
    """Raised when a tool execution is denied or fails."""


class MCPToolHandler:
    def __init__(self, use_case: RequestActionUseCase) -> None:
        self._use_case = use_case

    async def read_document(self, document_id: str, actor_id: str = "mcp-agent") -> str:
        command = RequestActionCommand(
            request_id=str(uuid4()),
            actor=Actor(actor_id=actor_id, actor_type=ActorType.AGENT, display_name="MCP Agent"),
            action=Action(
                action_type=ActionType.READ_CONTEXT,
                risk_level=RiskLevel.LOW,
                description=f"Read document via MCP: {document_id}",
            ),
        )

        result = await self._use_case.execute(command)

        if result.status != RequestActionStatus.ALLOWED:
            raise ToolExecutionError(f"Tool execution denied: {result.evaluation.reason}")

        if document_id not in _DOCUMENTS:
            raise ToolExecutionError(f"Document not found: {document_id}")

        return _DOCUMENTS[document_id]
