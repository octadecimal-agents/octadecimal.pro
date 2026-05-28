# Security Policy

Secure Agentic AI Platform is a security-first, portfolio-grade project for agentic AI workflows.

The project explores secure multi-step AI systems with human-in-the-loop approval, observability, audit trails, RAG, LLM evals, and prompt-injection defenses.

## Security Engineering Intent

This repository treats security as a core engineering concern, not as a final checklist.

The project is designed to demonstrate:

- secure-by-default local runtime boundaries,
- explicit human approval for risky agent actions,
- auditable policy and execution flows,
- prompt-injection-aware LLM workflows,
- careful handling of secrets and observability data,
- evaluation-driven validation of AI behavior.

## Security Learning Goals

This project is also a practical security engineering exercise.

Security-related contributions should make the maintainer better at:

- identifying trust boundaries,
- designing least-privilege execution paths,
- writing tests for denied and approved behavior,
- treating prompts, retrieved documents, traces, and logs as possible attack surfaces,
- reasoning about agent tool access before implementation,
- explaining the security tradeoffs behind architecture decisions.

Security controls should be implemented in small, reviewable steps so their behavior can be understood, tested, and explained.

## Supported Versions

The project is in early architecture and implementation phase.

Only the `main` branch is considered supported for security review.

## Reporting Security Issues

Do not open public GitHub issues for sensitive vulnerabilities.

Report privately by contacting the repository owner through GitHub or another trusted private channel.

Please include:

- affected component,
- impact,
- reproduction steps,
- expected vs actual behavior,
- relevant logs with sensitive data removed,
- suggested mitigation, if known.

Do not include:

- API keys,
- tokens,
- passwords,
- private prompts,
- personal data,
- unredacted host snapshots,
- proprietary customer data.

## Security Scope

Security-sensitive areas include:

- HITL approval gates,
- policy evaluation,
- prompt-injection detection,
- LLM provider gateways,
- RAG ingestion and retrieval,
- audit event integrity,
- secret handling,
- local runtime installers,
- Docker and CI configuration,
- OpenTelemetry and Langfuse tracing data,
- self-correcting agent loops,
- tool-calling boundaries.

## Security Principles

The project follows these principles:

- deny by default,
- least privilege,
- no direct host access for agents,
- explicit human approval for risky actions,
- audit every security-relevant decision,
- no plaintext secrets in repositories,
- no private local evidence in public commits,
- structured data contracts over ad hoc parsing,
- repeatable local runtime setup,
- security tests and evals for high-risk behavior.

## Secret Handling

Never commit:

- `.env` files,
- access tokens,
- refresh tokens,
- API keys,
- SSH private keys,
- provider credentials,
- secret-manager credentials,
- local machine access tokens,
- unredacted logs containing sensitive data.

Use placeholders in documentation:

```text
EXAMPLE_API_KEY=replace-me
```

## Secret Manager Strategy

The intended secret-management backend for this project is Bitwarden Secrets Manager.

Secrets should be accessed through a narrow application boundary, not directly from domain logic or agent workflows. The expected model is:

- application code depends on an internal `SecretProvider` interface,
- Bitwarden-specific access is isolated in an infrastructure adapter,
- tests use fake or in-memory secret providers,
- local examples use placeholders only,
- secret values are never written to logs, traces, audit events, eval outputs, or screenshots,
- secret resolution is treated as a high-risk operation that may require policy checks or human approval depending on context.

The repository may contain configuration templates and documentation for Bitwarden integration, but must not contain real Bitwarden credentials, access tokens, project identifiers that should remain private, or exported secret values.

If a secret is accidentally committed:

1. Stop using it immediately.
2. Revoke or rotate it at the provider.
3. Remove it from the repository.
4. Document the incident and remediation.
5. Review whether history rewriting is required before public release.

## AI Safety And Prompt Injection

The project treats prompt injection as a first-class security risk.

Contributions that add or modify LLM workflows should consider:

- direct prompt injection,
- indirect prompt injection through retrieved documents,
- instruction hierarchy conflicts,
- tool abuse,
- data exfiltration attempts,
- malicious documents in RAG pipelines,
- unsafe self-correction loops,
- approval bypass attempts.

Security-sensitive LLM behavior should be covered by tests or evals.

## Human Approval Rules

Agents must not directly perform high-risk actions.

High-risk actions include:

- shell or host command execution,
- file writes outside approved workspaces,
- secret resolution,
- external network calls with sensitive data,
- sending email or notifications outside local test channels,
- modifying policies, bridge scripts, or approval logic,
- changing audit logs or evidence.

Such actions must go through an explicit approval path.

## Local Runtime Security

The macOS local runtime profile separates:

```text
Administrator -> system maintenance
Human         -> human approval and oversight
Agents        -> agent runtime
```

Expected properties:

- `Agents` has no administrator privileges.
- `Agents` has no SSH access.
- privileged bridge scripts are protected from agent writes.
- immutable baseline context is protected from agent writes.
- secret tooling is scoped to an administrative boundary.
- install evidence remains local unless explicitly redacted.

This local profile is a deployment and learning environment. The same security ideas should later map to application-level RBAC, service boundaries, database state, and CI/CD controls.

## Dependency Security

Dependencies should be reviewed before adoption.

For new dependencies, document:

- why the dependency is needed,
- whether it is runtime or development-only,
- license considerations,
- security implications,
- replacement or removal path.

Use official packages and pinned versions where practical.

## Audit And Observability Data

Audit and tracing data can be sensitive.

Before committing logs, traces, screenshots, or eval outputs, check for:

- prompts with private data,
- model responses with sensitive data,
- access tokens,
- machine names that should remain private,
- local usernames,
- file paths revealing private context,
- customer or business information.

Prefer synthetic examples in public documentation.

## Security Review Checklist

Before merging security-sensitive changes:

- [ ] The trust boundary is clear.
- [ ] Risky actions require approval.
- [ ] Denied paths are tested.
- [ ] Audit events are emitted for relevant decisions.
- [ ] No secrets are logged or committed.
- [ ] Prompt-injection implications are considered.
- [ ] RAG ingestion cannot silently promote untrusted instructions.
- [ ] Observability data is redacted where needed.
- [ ] Rollback or mitigation path is documented.
