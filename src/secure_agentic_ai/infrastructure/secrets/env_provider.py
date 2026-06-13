import os

from secure_agentic_ai.domain.secrets import SecretValue


class EnvSecretProvider:
    def __init__(self, prefix: str = "APP_SECRET_") -> None:
        self._prefix = prefix

    async def resolve(self, name: str) -> SecretValue:
        env_key = f"{self._prefix}{name.upper().replace('-', '_')}"
        value = os.environ.get(env_key)
        if value is None:
            raise KeyError(f"Environment variable {env_key} not set")
        return SecretValue(name=name, _value=value)
