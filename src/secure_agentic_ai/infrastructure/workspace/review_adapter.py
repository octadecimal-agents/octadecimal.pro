from secure_agentic_ai.application.review_queue import PendingReviewItem
from secure_agentic_ai.domain.approvals import ApprovalRequest


def pending_review_items(requests: list[ApprovalRequest]) -> tuple[PendingReviewItem, ...]:
    return tuple(
        PendingReviewItem(
            request_id=req.request_id,
            description=req.action.description,
            actor_display_name=req.requested_by.display_name,
            risk_level=req.action.risk_level.value,
            action_type=req.action.action_type.value,
        )
        for req in requests
    )
