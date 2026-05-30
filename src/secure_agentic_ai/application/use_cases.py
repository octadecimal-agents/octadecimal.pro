from dataclasses import dataclass
from enum import StrEnum

from secure_agentic_ai.application.commands import RequestActionCommand
from secure_agentic_ai.application.ports import ApprovalRequestRepository, AuditWriter
from secure_agentic_ai.domain.approvals import ApprovalRequest
from secure_agentic_ai.domain.policies import (
    PolicyDecision,
    PolicyEvaluation,
    evaluate_policy,
)


class RequestActionStatus(StrEnum):
    ALLOWED = "allowed"
    APPROVAL_REQUIRED = "approval_required"
    DENIED = "denied"


@dataclass(frozen=True)
class RequestActionResult:
    status: RequestActionStatus
    evaluation: PolicyEvaluation
    approval_request: ApprovalRequest | None = None


class RequestActionUseCase:
    def __init__(
        self,
        request_repository: ApprovalRequestRepository,
        audit_writer: AuditWriter,
    ) -> None:
        self.request_repository = request_repository
        self.audit_writer = audit_writer

    def execute(self, command: RequestActionCommand) -> RequestActionResult:
        evaluation = evaluate_policy(command.actor, command.action)

        match evaluation.decision:
            case PolicyDecision.ALLOW:
                self.audit_writer.record(f"Action {command.action.action_type} allowed for {command.actor.actor_id}")
                return RequestActionResult(
                    status=RequestActionStatus.ALLOWED,
                    evaluation=evaluation,
                )

            case PolicyDecision.REQUIRE_APPROVAL:
                approval_request = ApprovalRequest(
                    request_id=command.request_id,
                    action=command.action,
                    requested_by=command.actor,
                )
                self.request_repository.save(approval_request)
                self.audit_writer.record(
                    f"Approval required for action {command.action.action_type} by {command.actor.actor_id}"
                )
                return RequestActionResult(
                    status=RequestActionStatus.APPROVAL_REQUIRED,
                    evaluation=evaluation,
                    approval_request=approval_request,
                )

            case PolicyDecision.DENY:
                self.audit_writer.record(f"Action {command.action.action_type} denied for {command.actor.actor_id}")
                return RequestActionResult(
                    status=RequestActionStatus.DENIED,
                    evaluation=evaluation,
                )
