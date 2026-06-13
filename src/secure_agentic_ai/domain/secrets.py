from dataclasses import dataclass


@dataclass(frozen=True)
class SecretValue:
    name: str
    _value: str

    def resolve(self) -> str:
        return self._value

    def __str__(self) -> str:
        return "****"

    def __repr__(self) -> str:
        return f"SecretValue(name={self.name!r})"
