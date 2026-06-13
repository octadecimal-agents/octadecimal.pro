from secure_agentic_ai.domain.safety import SafetyRiskLevel, SafetyVerdict
from secure_agentic_ai.infrastructure.security.injection_patterns import (
    DIRECT_INJECTION_PATTERNS,
    INDIRECT_INJECTION_PATTERNS,
    compile_patterns,
)


class PatternSafetyChecker:
    def __init__(self) -> None:
        self._direct_patterns = compile_patterns(DIRECT_INJECTION_PATTERNS)
        self._indirect_patterns = compile_patterns(INDIRECT_INJECTION_PATTERNS)

    async def check(self, content: str) -> SafetyVerdict:
        matched: list[str] = []

        for name, pattern, reason in self._direct_patterns:
            if pattern.search(content):
                matched.append(f"[direct:{name}] {reason}")

        for name, pattern, reason in self._indirect_patterns:
            if pattern.search(content):
                matched.append(f"[indirect:{name}] {reason}")

        if matched:
            has_dangerous = any(m.startswith("[direct:") for m in matched)
            return SafetyVerdict(
                is_safe=False,
                risk_level=SafetyRiskLevel.DANGEROUS if has_dangerous else SafetyRiskLevel.SUSPICIOUS,
                matched_patterns=matched,
                reason="; ".join(matched),
            )

        return SafetyVerdict(is_safe=True, risk_level=SafetyRiskLevel.SAFE, reason="No safety concerns detected")
