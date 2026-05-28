# Contributing

This document defines the engineering standards used in Secure Agentic AI Platform.

The project is built as a portfolio-grade agentic AI system, but it also serves a second purpose: deliberate, code-first growth in Python engineering. Contributions should make the system more understandable, testable, observable, and secure.

## Engineering Intent

This project should demonstrate that AI-assisted development can still be rigorous software engineering.

The expected working style is:

- small, reviewable changes,
- explicit architecture decisions,
- clear Python code,
- tests for important behavior,
- security and observability treated as core features,
- AI assistance used as a learning and review tool, not as a substitute for ownership.

## Code-First Learning Discipline

The maintainer uses this project to strengthen hands-on Python skills.

Rules:

1. Core domain logic should be understood before it is committed.
2. AI-assisted changes must be reviewed, explained, and owned by the maintainer.
3. Prefer small vertical slices over large generated scaffolds.
4. Avoid adding abstractions before the domain pressure justifies them.
5. Write or update tests before treating behavior as complete.
6. Keep implementation notes close to the code when a concept is new or subtle.
7. Be able to explain each committed module, test, and architectural decision.

## AI-Assisted Development Policy

AI tools may support:

- research,
- design alternatives,
- code review,
- debugging,
- test generation,
- refactoring suggestions,
- documentation drafts.

AI tools must not be treated as the source of truth.

Every committed change should be:

- understood by the maintainer,
- reviewed for security and correctness,
- covered by tests or explicit verification steps,
- consistent with the architecture of the project.

## Git Workflow

### Branching Strategy

```text
main --------------------------------> stable baseline
  |
  +-- feature/<short-description> ----> PR -> review -> merge
  +-- fix/<short-description> --------> PR -> review -> merge
  +-- test/<short-description> -------> PR -> review -> merge
  +-- docs/<short-description> -------> PR -> review -> merge
  +-- refactor/<short-description> ---> PR -> review -> merge
```

### Branch Naming

Use short, lowercase, hyphen-separated names:

```bash
feature/hitl-approval-api
feature/rag-retrieval-pipeline
feature/langgraph-agent-loop
fix/prompt-injection-classifier
fix/audit-event-schema
test/policy-engine-evals
docs/macos-runtime-model
refactor/domain-events
```

## Commit Convention

Use Conventional Commits:

```text
<type>(<scope>): <description>

[optional body]
```

### Types

| Type | Meaning |
| --- | --- |
| `feat` | New capability |
| `fix` | Bug fix |
| `refactor` | Internal change without intended behavior change |
| `docs` | Documentation |
| `test` | Tests or evals |
| `chore` | Tooling, configuration, housekeeping |
| `style` | Formatting only |
| `security` | Security hardening or security policy change |

### Suggested Scopes

```text
api
domain
policy
approval
audit
evals
rag
langgraph
observability
security
docker
docs
macos
ci
```

### Examples

```bash
docs(macos): describe local runtime account model
feat(approval): add HITL request state machine
feat(rag): add retrieval pipeline interface
test(policy): cover denied host-action scenarios
security(prompt): block indirect injection patterns
chore(ci): add Python test workflow
```

### Rules

1. One commit should represent one logical change.
2. Commit messages should be written in English.
3. Keep the first line under 72 characters when practical.
4. Do not end the commit subject with a period.
5. Do not mix unrelated docs, code, tests, and formatting changes.

## Quality Gates

Before a pull request is considered ready, run the relevant checks for the changed area.

The exact commands will evolve with the implementation. The expected baseline is:

```bash
ruff check .
ruff format --check .
mypy .
pytest
```

For frontend or browser-facing changes:

```bash
npm test
npx playwright test
```

For LLM workflow changes:

```bash
pytest tests/evals
```

If a check is not available yet, document that in the pull request test plan.

## Testing Strategy

The project should use multiple layers of verification:

```text
tests/
├── unit/          # isolated domain and policy tests
├── integration/   # API, database, queue, and service boundaries
├── e2e/           # user-visible flows and browser/API journeys
└── evals/         # LLM behavior, RAG quality, and safety evaluations
```

### Testing Rules

1. Domain and policy behavior should have unit tests.
2. Security fixes should include regression tests or explicit verification steps.
3. Approval and audit flows must test both allowed and denied paths.
4. LLM workflows should include deterministic tests where possible and evals where behavior is model-dependent.
5. RAG changes should test retrieval quality and prompt-injection resistance.
6. New external integrations should be isolated behind interfaces/adapters.

## Documentation

Documentation should be written in English.

Use documentation to explain:

- why a decision exists,
- what risks it reduces,
- how to verify it,
- what is intentionally not implemented yet.

Prefer small, focused documents over one large narrative file.

Suggested locations:

```text
docs/architecture/
docs/deployment/
docs/security/
docs/evals/
docs/operations/
```

## Python Coding Standards

Expected conventions:

| Element | Convention | Example |
| --- | --- | --- |
| Module | snake_case | `approval_service.py` |
| Package | snake_case | `agentic_platform` |
| Class | PascalCase | `ApprovalRequest` |
| Function | snake_case | `create_approval_request()` |
| Variable | snake_case | `risk_level` |
| Constant | UPPER_SNAKE_CASE | `MAX_RETRIES` |

Use:

- Python 3.12 or newer,
- Pydantic v2 for data contracts,
- typed domain models,
- explicit dependency boundaries,
- clear errors over silent failure.

Avoid:

- hidden global state,
- direct provider calls from domain logic,
- hardcoded credentials,
- ad hoc parsing when structured parsing is available,
- untested security-sensitive behavior.

## Pull Requests

Pull requests should include:

```markdown
## Summary
- What changed and why.

## Changed Files
- `path/to/file.py` - concise explanation.

## Technical Decisions
- Important tradeoffs or architecture notes.

## Security Notes
- New risks, mitigations, or affected trust boundaries.

## Learning Notes
- What was clarified, practiced, or deliberately implemented code-first.

## Test Plan
- [ ] Unit tests pass.
- [ ] Integration tests pass, if applicable.
- [ ] Evals updated or not required.
- [ ] No secrets or private local evidence included.
```

## Merge Checklist

- [ ] The change is small enough to review.
- [ ] Commit messages follow the convention.
- [ ] Tests or verification steps are documented.
- [ ] Security-sensitive behavior has explicit review.
- [ ] No credentials, tokens, `.env` files, private snapshots, or local evidence are committed.
- [ ] Documentation is updated when architecture or behavior changes.
- [ ] The maintainer can explain the committed implementation.

