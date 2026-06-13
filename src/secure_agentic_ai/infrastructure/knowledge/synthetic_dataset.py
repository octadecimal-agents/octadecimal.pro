DOCUMENTS: list[str] = [
    "The secure agentic AI platform provides governance for autonomous agents. "
    "Every action must pass through a policy evaluation before execution. "
    "Human approval is required for high-risk actions such as writing files or resolving secrets.",
    "Policy evaluation checks the actor type and risk level of each action. "
    "Low-risk actions by human actors are allowed automatically. "
    "High-risk actions by agents always require human-in-the-loop approval.",
    "The audit trail records every policy decision and action execution. "
    "Each audit event includes an event type, actor identifier, action type, and timestamp. "
    "Audit events are immutable and stored in the persistence layer.",
    "Approval requests are created when a policy requires human judgment. "
    "An approval request can be approved, rejected, or left pending. "
    "Once decided, the approval status cannot be changed.",
]
