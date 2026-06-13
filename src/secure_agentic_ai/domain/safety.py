from dataclasses import dataclass, field
from enum import StrEnum


class SafetyRiskLevel(StrEnum):
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    DANGEROUS = "dangerous"


@dataclass(frozen=True)
class SafetyVerdict:
    is_safe: bool
    risk_level: SafetyRiskLevel = SafetyRiskLevel.SAFE
    matched_patterns: list[str] = field(default_factory=list)
    reason: str = ""
