from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import yaml

from secure_agentic_ai.infrastructure.workspace.config import WorkspaceConfig


@dataclass(frozen=True)
class KnowledgeTierPolicy:
    include: tuple[str, ...]
    exclude: tuple[str, ...]


@dataclass(frozen=True)
class KnowledgePolicy:
    tiers: dict[str, KnowledgeTierPolicy]
    retrieval_weights: dict[str, float] | None = None


def policy_path(config: WorkspaceConfig) -> Path:
    return config.knowledge_root / ".knowledge-index" / "policy.yaml"


def _as_str_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(str(item).strip() for item in value if str(item).strip())


def load_knowledge_policy(config: WorkspaceConfig) -> KnowledgePolicy | None:
    path = policy_path(config)
    if not path.is_file():
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None
    if not isinstance(data, dict):
        return None

    tiers_raw = data.get("tiers")
    if not isinstance(tiers_raw, dict):
        return None

    tiers: dict[str, KnowledgeTierPolicy] = {}
    for tier_name, tier_data in tiers_raw.items():
        if not isinstance(tier_data, dict):
            continue
        tiers[str(tier_name)] = KnowledgeTierPolicy(
            include=_as_str_tuple(tier_data.get("include")),
            exclude=_as_str_tuple(tier_data.get("exclude")),
        )

    retrieval_weights: dict[str, float] | None = None
    retrieval = data.get("retrieval")
    if isinstance(retrieval, dict):
        weights = retrieval.get("weights")
        if isinstance(weights, dict):
            parsed: dict[str, float] = {}
            for key, value in weights.items():
                if isinstance(value, (int, float)):
                    parsed[str(key)] = float(value)
            if parsed:
                retrieval_weights = parsed

    if not tiers:
        return None
    return KnowledgePolicy(tiers=tiers, retrieval_weights=retrieval_weights)


def effective_scan_globs(config: WorkspaceConfig) -> tuple[str, ...]:
    """Return include globs for active tiers (non-empty include lists)."""
    policy = load_knowledge_policy(config)
    if policy is None:
        return config.knowledge_globs

    globs: list[str] = []
    for tier in policy.tiers.values():
        if tier.include:
            globs.extend(tier.include)
    return tuple(globs) if globs else config.knowledge_globs


def effective_exclude_globs(config: WorkspaceConfig) -> tuple[str, ...]:
    policy = load_knowledge_policy(config)
    if policy is None:
        return ()

    excludes: list[str] = []
    for tier in policy.tiers.values():
        excludes.extend(tier.exclude)
    return tuple(excludes)


def path_matches_pattern(relative_posix_path: str, pattern: str) -> bool:
    return PurePosixPath(relative_posix_path).match(pattern)


def is_path_excluded(relative_posix_path: str, exclude_patterns: tuple[str, ...]) -> bool:
    return any(path_matches_pattern(relative_posix_path, pattern) for pattern in exclude_patterns)


@dataclass(frozen=True)
class RetrievalWeights:
    vector: float = 0.25
    path: float = 0.75
    heading: float = 0.0
    recency: float = 0.0


_DEFAULT_V2_WEIGHTS = RetrievalWeights(vector=0.6, path=0.25, heading=0.1, recency=0.05)


def retrieval_weights_from_policy(policy: KnowledgePolicy | None) -> RetrievalWeights:
    if policy is None:
        return RetrievalWeights()
    if not policy.retrieval_weights:
        return _DEFAULT_V2_WEIGHTS
    weights = policy.retrieval_weights
    return RetrievalWeights(
        vector=float(weights.get("vector", _DEFAULT_V2_WEIGHTS.vector)),
        path=float(weights.get("path", _DEFAULT_V2_WEIGHTS.path)),
        heading=float(weights.get("heading", _DEFAULT_V2_WEIGHTS.heading)),
        recency=float(weights.get("recency", _DEFAULT_V2_WEIGHTS.recency)),
    )


def effective_retrieval_weights(config: WorkspaceConfig) -> RetrievalWeights:
    return retrieval_weights_from_policy(load_knowledge_policy(config))
