from secure_agentic_ai.domain.observability import CostEstimate, TokenUsage

DEFAULT_MODEL = "default"

MODEL_PRICING: dict[str, tuple[float, float]] = {
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "claude-3.5-sonnet": (3.00, 15.00),
    "claude-3-haiku": (0.25, 1.25),
    DEFAULT_MODEL: (1.00, 4.00),
}


class CostCalculator:
    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model

    def estimate(self, usage: TokenUsage) -> CostEstimate:
        per_1k_input, per_1k_output = MODEL_PRICING.get(self.model, MODEL_PRICING[DEFAULT_MODEL])
        input_cost = (usage.input_tokens / 1000) * per_1k_input
        output_cost = (usage.output_tokens / 1000) * per_1k_output
        return CostEstimate(
            total_usd=round(input_cost + output_cost, 6),
            input_cost_usd=round(input_cost, 6),
            output_cost_usd=round(output_cost, 6),
            model=self.model,
        )
