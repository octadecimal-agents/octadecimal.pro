from dataclasses import dataclass, field
from datetime import UTC, datetime


class TokenUsage:
    def __init__(self, input_tokens: int = 0, output_tokens: int = 0) -> None:
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens

    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass(frozen=True)
class CostEstimate:
    total_usd: float
    input_cost_usd: float = 0.0
    output_cost_usd: float = 0.0
    model: str = ""


@dataclass(frozen=True)
class EvalCase:
    name: str
    description: str
    expected_status: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "description": self.description, "expected_status": self.expected_status}


@dataclass(frozen=True)
class EvalResult:
    case: EvalCase
    passed: bool
    actual_status: str
    duration_ms: float = 0.0
    error: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
