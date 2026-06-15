import json
import logging

from secure_agentic_ai.application.workspace_tools import ToolResult

logger = logging.getLogger("secure_agentic_ai.workspace_agent")


def log_tool_trace(message: str, trace: list[ToolResult]) -> None:
    if not trace:
        return
    payload = {
        "event": "tool_trace",
        "message": message,
        "tools": [
            {
                "name": item.name,
                "duration_ms": item.duration_ms,
                "rows": item.row_count,
            }
            for item in trace
        ],
    }
    logger.info(json.dumps(payload, ensure_ascii=False))
