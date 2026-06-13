from functools import partial
from typing import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import interrupt

from secure_agentic_ai.application.commands import RequestActionCommand
from secure_agentic_ai.application.use_cases import (
    RequestActionResult,
    RequestActionStatus,
    RequestActionUseCase,
)


class HITLWorkflowState(TypedDict):
    command: RequestActionCommand
    policy_result: RequestActionResult | None
    approval_decision: str | None


async def policy_check_node(state: HITLWorkflowState, use_case: RequestActionUseCase) -> HITLWorkflowState:
    result = await use_case.execute(state["command"])
    return HITLWorkflowState(
        command=state["command"],
        policy_result=result,
        approval_decision=None,
    )


async def human_review_node(state: HITLWorkflowState) -> HITLWorkflowState:
    decision = interrupt("Waiting for human approval")
    return HITLWorkflowState(
        command=state["command"],
        policy_result=state["policy_result"],
        approval_decision=decision,
    )


async def execute_action_node(state: HITLWorkflowState) -> HITLWorkflowState:
    return state


def route_after_policy(state: HITLWorkflowState) -> str:
    result = state["policy_result"]
    if result is None:
        return "deny"
    match result.status:
        case RequestActionStatus.ALLOWED:
            return "allow"
        case RequestActionStatus.DENIED:
            return "deny"
        case RequestActionStatus.APPROVAL_REQUIRED:
            return "require_approval"


def route_after_review(state: HITLWorkflowState) -> str:
    decision = state.get("approval_decision")
    if decision == "approved":
        return "approved"
    return "rejected"


def build_hitl_workflow(use_case: RequestActionUseCase) -> CompiledStateGraph[HITLWorkflowState]:
    builder = StateGraph(HITLWorkflowState)

    builder.add_node("policy_check", partial(policy_check_node, use_case=use_case))
    builder.add_node("human_review", human_review_node)
    builder.add_node("execute_action", execute_action_node)

    builder.set_entry_point("policy_check")

    builder.add_conditional_edges(
        "policy_check",
        route_after_policy,
        {
            "allow": "execute_action",
            "deny": END,
            "require_approval": "human_review",
        },
    )

    builder.add_conditional_edges(
        "human_review",
        route_after_review,
        {
            "approved": "execute_action",
            "rejected": END,
        },
    )

    builder.add_edge("execute_action", END)

    return builder.compile(checkpointer=MemorySaver())
