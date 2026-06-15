# MCP Workspace — read-only tool policy (M5.4.4)
#
# Allowed: calendar, wiki, board list, review summary, health metadata.
# Denied:  task create/update, HITL approve/reject, any write without human UI.
#
# Future write tools MUST go through governance policy + HITL before registration here.

READ_ONLY_TOOL_NAMES: frozenset[str] = frozenset(
    {
        "list_today_calendar",
        "workspace_health",
        "wiki_search",
        "board_list_tasks",
        "review_pending_summary",
    }
)

FORBIDDEN_WRITE_TOOL_NAMES: frozenset[str] = frozenset(
    {
        "approve_review",
        "board_create_task",
        "board_update_task",
        "review_approve",
        "review_reject",
    }
)
