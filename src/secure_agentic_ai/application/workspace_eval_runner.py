from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from secure_agentic_ai.application.chat_reply import ChatReply


@dataclass(frozen=True)
class ChatEvalCase:
    case_id: str
    input: str
    expected_hash: str | None
    message_contains: tuple[str, ...]


@dataclass(frozen=True)
class RagEvalCase:
    case_id: str
    query: str
    expected_source_suffix: str
    top_k: int = 3


@dataclass(frozen=True)
class EvalCaseResult:
    case_id: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class EvalReport:
    total: int
    passed: int
    results: tuple[EvalCaseResult, ...]

    @property
    def pass_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.passed / self.total


def load_chat_eval_cases(path: Path) -> list[ChatEvalCase]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Invalid chat eval file: {path}")
    raw_cases = data.get("cases")
    if not isinstance(raw_cases, list):
        raise ValueError(f"Missing cases in chat eval file: {path}")

    cases: list[ChatEvalCase] = []
    for item in raw_cases:
        if not isinstance(item, dict):
            continue
        expect = item.get("expect")
        if not isinstance(expect, dict):
            continue
        contains = expect.get("message_contains", [])
        if not isinstance(contains, list):
            contains = []
        cases.append(
            ChatEvalCase(
                case_id=str(item.get("id", "")),
                input=str(item.get("input", "")),
                expected_hash=str(expect["suggested_hash"]) if expect.get("suggested_hash") else None,
                message_contains=tuple(str(part) for part in contains),
            )
        )
    return cases


def load_rag_eval_cases(path: Path) -> list[RagEvalCase]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Invalid RAG eval file: {path}")
    raw_cases = data.get("cases")
    if not isinstance(raw_cases, list):
        raise ValueError(f"Missing cases in RAG eval file: {path}")

    cases: list[RagEvalCase] = []
    for item in raw_cases:
        if not isinstance(item, dict):
            continue
        expect = item.get("expect")
        if not isinstance(expect, dict):
            continue
        cases.append(
            RagEvalCase(
                case_id=str(item.get("id", "")),
                query=str(item.get("query", "")),
                expected_source_suffix=str(expect.get("source_suffix", "")),
                top_k=int(expect.get("top_k", 3)),
            )
        )
    return cases


def evaluate_chat_case(case: ChatEvalCase, reply: ChatReply) -> EvalCaseResult:
    failures: list[str] = []
    if case.expected_hash and reply.suggested_hash != case.expected_hash:
        failures.append(f"hash={reply.suggested_hash!r} expected {case.expected_hash!r}")
    for needle in case.message_contains:
        if needle.lower() not in reply.message.lower():
            failures.append(f"missing {needle!r} in message")
    if failures:
        return EvalCaseResult(case_id=case.case_id, passed=False, detail="; ".join(failures))
    return EvalCaseResult(case_id=case.case_id, passed=True, detail="ok")


def evaluate_rag_case(
    case: RagEvalCase,
    sources: list[str],
) -> EvalCaseResult:
    top_sources = sources[: case.top_k]
    if any(case.expected_source_suffix in source for source in top_sources):
        return EvalCaseResult(case_id=case.case_id, passed=True, detail="ok")
    return EvalCaseResult(
        case_id=case.case_id,
        passed=False,
        detail=f"top-{case.top_k}={top_sources!r} expected *{case.expected_source_suffix}",
    )


def summarize_results(results: list[EvalCaseResult]) -> EvalReport:
    passed = sum(1 for item in results if item.passed)
    return EvalReport(total=len(results), passed=passed, results=tuple(results))


def format_report(title: str, report: EvalReport) -> str:
    lines = [title, f"pass_rate={report.pass_rate:.0%} ({report.passed}/{report.total})"]
    for item in report.results:
        status = "PASS" if item.passed else "FAIL"
        lines.append(f"  [{status}] {item.case_id}: {item.detail}")
    return "\n".join(lines)


def parse_min_pass_rate(value: Any, default: float = 0.8) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return default
