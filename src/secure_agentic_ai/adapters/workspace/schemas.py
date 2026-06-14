from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    active_hash: str | None = None


class ChatResponse(BaseModel):
    message: str
    suggested_hash: str | None = None
    citations: list[str] = Field(default_factory=list)


class TaskCreateRequest(BaseModel):
    team: str
    title: str = Field(min_length=1, max_length=500)
    intent: str | None = None
    status: str = "todo"


class TaskUpdateRequest(BaseModel):
    status: str


class TaskResponse(BaseModel):
    id: str
    team: str
    status: str
    title: str
    intent: str | None
    created_at: str
    updated_at: str


class PlanItemRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    source: str = "ceo"


class PlanReplaceRequest(BaseModel):
    plan_date: str
    items: list[PlanItemRequest]


class PlanItemResponse(BaseModel):
    id: int
    plan_date: str
    sort_order: int
    title: str
    source: str


class WikiSearchResponse(BaseModel):
    query: str
    results: list[dict[str, str | float]]


class ApprovalSummary(BaseModel):
    request_id: str
    description: str
    actor_display_name: str
    risk_level: str
    action_type: str


class RetroRequest(BaseModel):
    went_well: str = Field(min_length=1, max_length=2000)
    improve: str = Field(min_length=1, max_length=2000)
    tomorrow: str = Field(min_length=1, max_length=2000)


class RetroResponse(BaseModel):
    path: str
    content: str


class RetroTodayResponse(BaseModel):
    path: str
    content: str | None = None


class CalendarEvent(BaseModel):
    time: str
    title: str
    calendar: str | None = None


class CalendarListResponse(BaseModel):
    source: str
    events: list[CalendarEvent]


class HealthWorkspaceResponse(BaseModel):
    status: str
    knowledge_root: str
    ledger_path: str
    documents_indexed: int
    rag_backend: str
    llm_provider: str
    review_pending_count: int = 0
