import pytest

from secure_agentic_ai.application.commands import ResolveSecretCommand
from secure_agentic_ai.application.use_cases import (
    ResolveSecretUseCase,
    SecretResolveStatus,
)
from secure_agentic_ai.domain.actors import Actor, ActorType
from secure_agentic_ai.domain.secrets import SecretValue
from secure_agentic_ai.infrastructure.secrets.env_provider import EnvSecretProvider
from secure_agentic_ai.infrastructure.secrets.fake_provider import FakeSecretProvider


class FakeAuditWriter:
    def __init__(self) -> None:
        self.events = []

    async def record(self, event) -> None:
        self.events.append(event)


@pytest.fixture
def audit_writer():
    return FakeAuditWriter()


# --- SecretValue domain model ---


def test_secret_value_masks_str():
    sv = SecretValue(name="api-key", _value="supersecret123")
    assert str(sv) == "****"
    assert "supersecret123" not in str(sv)


def test_secret_value_masks_repr():
    sv = SecretValue(name="db-password", _value="s3cret!")
    r = repr(sv)
    assert "db-password" in r
    assert "s3cret!" not in r


def test_secret_value_resolve_returns_value():
    sv = SecretValue(name="api-key", _value="real-value")
    assert sv.resolve() == "real-value"


# --- FakeSecretProvider ---


@pytest.mark.asyncio
async def test_fake_provider_resolves_known_secret():
    provider = FakeSecretProvider()
    sv = await provider.resolve("api-key")
    assert sv.resolve() == "sk-fake-test-key-12345"


@pytest.mark.asyncio
async def test_fake_provider_raises_on_unknown():
    provider = FakeSecretProvider()
    with pytest.raises(KeyError, match="Secret not found"):
        await provider.resolve("nonexistent")


# --- EnvSecretProvider ---


@pytest.mark.asyncio
async def test_env_provider_reads_from_environment(monkeypatch):
    monkeypatch.setenv("APP_SECRET_API_KEY", "env-secret-value")
    provider = EnvSecretProvider()
    sv = await provider.resolve("api-key")
    assert sv.resolve() == "env-secret-value"


@pytest.mark.asyncio
async def test_env_provider_raises_when_missing():
    provider = EnvSecretProvider()
    with pytest.raises(KeyError, match="not set"):
        await provider.resolve("missing-key")


# --- ResolveSecretUseCase ---


@pytest.mark.asyncio
async def test_use_case_resolves_for_human(audit_writer):
    provider = FakeSecretProvider()
    use_case = ResolveSecretUseCase(secret_provider=provider, audit_writer=audit_writer)

    command = ResolveSecretCommand(
        secret_name="api-key",
        actor=Actor(actor_id="human-001", actor_type=ActorType.HUMAN, display_name="Operator"),
    )

    result = await use_case.execute(command)

    assert result.status == SecretResolveStatus.RESOLVED
    assert result.value is not None
    assert result.value.resolve() == "sk-fake-test-key-12345"


@pytest.mark.asyncio
async def test_use_case_denies_agent(audit_writer):
    provider = FakeSecretProvider()
    use_case = ResolveSecretUseCase(secret_provider=provider, audit_writer=audit_writer)

    command = ResolveSecretCommand(
        secret_name="api-key",
        actor=Actor(actor_id="agent-001", actor_type=ActorType.AGENT, display_name="Agent"),
    )

    result = await use_case.execute(command)

    assert result.status == SecretResolveStatus.DENIED
    assert result.value is None
    assert "Agents cannot resolve secrets" in result.evaluation.reason


@pytest.mark.asyncio
async def test_audit_event_does_not_contain_secret_value(audit_writer):
    provider = FakeSecretProvider()
    use_case = ResolveSecretUseCase(secret_provider=provider, audit_writer=audit_writer)

    command = ResolveSecretCommand(
        secret_name="api-key",
        actor=Actor(actor_id="human-001", actor_type=ActorType.HUMAN, display_name="Operator"),
    )

    await use_case.execute(command)

    assert len(audit_writer.events) == 1
    event = audit_writer.events[0]
    assert event.action_type == "secret.resolve"
    assert event.metadata.get("secret_name") == "api-key"
    assert "sk-fake" not in str(event.metadata)


@pytest.mark.asyncio
async def test_audit_logs_denied_for_agent(audit_writer):
    provider = FakeSecretProvider()
    use_case = ResolveSecretUseCase(secret_provider=provider, audit_writer=audit_writer)

    command = ResolveSecretCommand(
        secret_name="api-key",
        actor=Actor(actor_id="agent-001", actor_type=ActorType.AGENT, display_name="Agent"),
    )

    await use_case.execute(command)

    assert len(audit_writer.events) == 1
    assert audit_writer.events[0].event_type.value == "action.denied"


@pytest.mark.asyncio
async def test_audit_logs_resolved_for_human(audit_writer):
    provider = FakeSecretProvider()
    use_case = ResolveSecretUseCase(secret_provider=provider, audit_writer=audit_writer)

    command = ResolveSecretCommand(
        secret_name="api-key",
        actor=Actor(actor_id="human-001", actor_type=ActorType.HUMAN, display_name="Operator"),
    )

    await use_case.execute(command)

    assert len(audit_writer.events) == 1
    assert audit_writer.events[0].event_type.value == "action.allowed"
