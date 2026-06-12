from pydantic import BaseModel, ConfigDict, Field

from secure_agentic_ai.application.commands import RequestActionCommand
from secure_agentic_ai.application.use_cases import RequestActionResult
from secure_agentic_ai.domain.actors import Actor, ActorType
from secure_agentic_ai.domain.policies import Action, ActionType, RiskLevel


class RequestActionPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(
        min_length=1,
        max_length=120,
        description="Client-generated request identifier used for audit correlation.",
        examples=["req-001"],
    )
    actor_id: str = Field(
        min_length=1,
        max_length=120,
        description="Identifier of the human or agent requesting the action.",
        examples=["agent-001"],
    )
    actor_type: ActorType = Field(
        description="Type of actor that requests the action.",
        examples=[ActorType.AGENT],
    )
    actor_display_name: str = Field(
        min_length=1,
        max_length=200,
        description="Human-readable actor name for audit and debugging.",
        examples=["Developer Agent"],
    )
    action_type: ActionType = Field(
        description="Type of requested action.",
        examples=[ActionType.WRITE_FILE],
    )
    risk_level: RiskLevel = Field(
        description="Declared risk level for the requested action.",
        examples=[RiskLevel.HIGH],
    )
    action_description: str = Field(
        min_length=1,
        max_length=500,
        description="Short explanation of what the actor wants to do.",
        examples=["Write generated source file"],
    )

    def to_command(self) -> RequestActionCommand:
        return RequestActionCommand(
            request_id=self.request_id,
            actor=Actor(
                actor_id=self.actor_id,
                actor_type=self.actor_type,
                display_name=self.actor_display_name,
            ),
            action=Action(
                action_type=self.action_type,
                risk_level=self.risk_level,
                description=self.action_description,
            ),
        )


class RequestActionResponse(BaseModel):
    status: str = Field(description="Application-level outcome of the request.")
    decision: str = Field(description="Policy decision produced by the domain.")
    reason: str = Field(description="Human-readable explanation of the decision.")
    approval_request_id: str | None = Field(
        default=None,
        description="Approval request identifier when human approval is required.",
    )

    @classmethod
    def from_result(cls, result: RequestActionResult) -> "RequestActionResponse":
        return cls(
            status=result.status.value,
            decision=result.evaluation.decision.value,
            reason=result.evaluation.reason,
            approval_request_id=(result.approval_request.request_id if result.approval_request is not None else None),
        )


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])
