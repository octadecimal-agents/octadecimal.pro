from dataclasses import dataclass

from secure_agentic_ai.domain.actors import Actor
from secure_agentic_ai.domain.policies import Action


@dataclass(frozen=True)
class RequestActionCommand:
    request_id: str
    actor: Actor
    action: Action


@dataclass(frozen=True)
class ResolveSecretCommand:
    secret_name: str
    actor: Actor
