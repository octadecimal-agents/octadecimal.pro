from secure_agentic_ai.domain.secrets import SecretValue


class FakeSecretProvider:
    def __init__(self) -> None:
        self._secrets: dict[str, str] = {
            "api-key": "sk-fake-test-key-12345",
            "db-password": "fake-db-pass-98765",
        }

    async def resolve(self, name: str) -> SecretValue:
        if name not in self._secrets:
            raise KeyError(f"Secret not found: {name}")
        return SecretValue(name=name, _value=self._secrets[name])
