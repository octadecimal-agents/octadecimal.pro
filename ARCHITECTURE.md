# Architecture

## Layer Diagram

```mermaid
graph TB
    subgraph "Adapters / Entry Points"
        API[FastAPI Router]
        OP[Operator Console<br/>Jinja2 Templates]
        MCP[MCP Server<br/>FastMCP]
    end

    subgraph "Application"
        P[Ports / Protocols]
        UC[Use Cases]
        CMD[Commands / Results]
    end

    subgraph "Domain"
        ACT[Actor]
        POL[Policy<br/>evaluate_policy]
        AR[ApprovalRequest<br/>state machine]
        AE[AuditEvent]
        SEC[SecretValue]
        DOC[DocumentChunk]
        SAFE[SafetyVerdict]
        OBS[TokenUsage / EvalResult]
    end

    subgraph "Infrastructure"
        DB[SQLAlchemy Async]
        LG[LangGraph HITL]
        RAG[FakeEmbedding / InMemoryVector]
        CHK[PatternSafetyChecker]
        TRC[DebugTracer / CostCalc / EvalRunner]
        PRV[Fake / Env / Bitwarden Providers]
        ALB[Alembic Migrations]
    end

    API --> UC
    OP --> UC
    MCP --> UC
    UC --> P
    UC --> CMD
    UC --> ACT
    UC --> POL
    UC --> AR
    UC --> AE
    UC --> SEC
    UC --> DOC
    UC --> SAFE
    UC --> OBS
    P --> DB
    P --> RAG
    P --> CHK
    P --> TRC
    P --> PRV
    LG --> UC
    DB --> ALB
```

## Request Flow (Approval)

```mermaid
sequenceDiagram
    participant C as Client / Agent
    participant A as FastAPI / MCP
    participant UC as Use Case
    participant P as Policy
    participant R as Repository
    participant W as Audit Writer

    C->>A: Request action
    A->>UC: execute(command)
    UC->>P: evaluate_policy(actor, action)
    alt ALLOW
        P-->>UC: ALLOW
        UC->>W: record(action.allowed)
        UC-->>A: Result(allowed)
    else DENY
        P-->>UC: DENY
        UC->>W: record(action.denied)
        UC-->>A: Result(denied)
    else REQUIRE_APPROVAL
        P-->>UC: REQUIRE_APPROVAL
        UC->>R: save(approval_request)
        UC->>W: record(approval.requested)
        UC-->>A: Result(approval_required)
    end
    A-->>C: Response
```

## HITL Workflow

```mermaid
stateDiagram-v2
    [*] --> PolicyCheck
    PolicyCheck --> Allowed: ALLOW
    PolicyCheck --> Blocked: DENY
    PolicyCheck --> HumanReview: APPROVAL_REQUIRED
    HumanReview --> Approved: resume("approved")
    HumanReview --> Rejected: resume("rejected")
    Approved --> ExecuteAction
    ExecuteAction --> [*]
    Allowed --> [*]
    Blocked --> [*]
    Rejected --> [*]
```

## Directory Map

```
src/secure_agentic_ai/
├── domain/                  # Pure domain
│   ├── actors.py            Actor dataclass
│   ├── policies.py          Policy decisions, ActionType, RiskLevel
│   ├── approvals.py         ApprovalRequest state machine
│   ├── audit.py             AuditEvent with trace support
│   ├── knowledge.py         DocumentChunk, RetrievedChunk
│   ├── safety.py            SafetyVerdict, SafetyRiskLevel
│   ├── secrets.py           SecretValue with masked repr
│   └── observability.py     TokenUsage, CostEstimate, EvalCase/Result
│
├── application/             # Use cases and ports
│   ├── commands.py          RequestActionCommand, ResolveSecretCommand
│   ├── ports.py             Protocols: ApprovalRequestRepository, AuditWriter,
│   │                        EmbeddingProvider, VectorStore, SafetyChecker,
│   │                        Tracer, AuditReader, SecretProvider
│   └── use_cases.py         RequestActionUseCase, ResolveSecretUseCase,
│                            IngestDocumentUseCase, RetrieveContextUseCase
│
├── adapters/api/            # FastAPI entry points
│   ├── app.py               FastAPI app factory with lifespan
│   ├── dependencies.py      DI: DB session, repos, use cases
│   ├── routes.py            /health, /actions endpoints
│   ├── schemas.py           Pydantic request/response schemas
│   ├── operator_router.py   /operator/ dashboard, approvals, audit
│   └── templates/           Jinja2 HTML templates
│
└── infrastructure/          # Concrete implementations
    ├── persistence/         SQLAlchemy async, Alembic migrations
    ├── workflows/           LangGraph HITL workflow
    ├── knowledge/           FakeEmbeddingProvider, InMemoryVectorStore
    ├── security/            PatternSafetyChecker, injection regexes
    ├── mcp/                 FastMCP server, tool handler
    ├── secrets/             Fake/Env/Bitwarden providers
    └── observability/       DebugTracer, CostCalculator, EvalRunner
```
