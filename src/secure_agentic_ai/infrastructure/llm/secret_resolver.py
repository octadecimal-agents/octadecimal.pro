import asyncio
import json
import os
import shutil
from pathlib import Path

from secure_agentic_ai.infrastructure.secrets.bitwarden_provider import BitwardenSecretProvider

DEFAULT_BWS_PROJECT = "multi-agents-framework-m1"
DEFAULT_BWS_DEEPSEEK_SECRET_KEY = "DEEPSEEK_API_KEY"
DEFAULT_BWS_MINIMAX_SECRET_KEY = "MINIMAX_API_TOKEN"


async def resolve_deepseek_api_key(
    *,
    knowledge_root: Path,
    bw_label: str,
    bws_project_name: str = DEFAULT_BWS_PROJECT,
    bws_secret_key: str = DEFAULT_BWS_DEEPSEEK_SECRET_KEY,
) -> str | None:
    """Resolve DeepSeek API key without logging the value."""
    return await _resolve_llm_token(
        env_keys=("DEEPSEEK_API_KEY",),
        knowledge_root=knowledge_root,
        bw_label=bw_label,
        manifest_key="deepseek_api_key",
        default_bw_label="octadecimal-infra/deepseek-api-key",
        bws_project_name=bws_project_name,
        bws_secret_key_env="BWS_DEEPSEEK_SECRET_KEY",
        bws_secret_key=bws_secret_key,
        bws_secret_id_env="BWS_DEEPSEEK_SECRET_ID",
        bw_secret_id_env="BW_SECRET_ID_DEEPSEEK_API_KEY",
        bitwarden_provider_key="deepseek_api_key",
    )


async def resolve_minimax_api_token(
    *,
    knowledge_root: Path,
    bw_label: str,
    bws_project_name: str = DEFAULT_BWS_PROJECT,
    bws_secret_key: str = DEFAULT_BWS_MINIMAX_SECRET_KEY,
) -> str | None:
    """Resolve MiniMax API token without logging the value."""
    return await _resolve_llm_token(
        env_keys=("MINIMAX_API_TOKEN", "MINIMAX_API_KEY"),
        knowledge_root=knowledge_root,
        bw_label=bw_label,
        manifest_key="minimax_api_token",
        default_bw_label="octadecimal-infra/minimax-api-token",
        bws_project_name=bws_project_name,
        bws_secret_key_env="BWS_MINIMAX_SECRET_KEY",
        bws_secret_key=bws_secret_key,
        bws_secret_id_env="BWS_MINIMAX_SECRET_ID",
        bw_secret_id_env="BW_SECRET_ID_MINIMAX_API_TOKEN",
        bitwarden_provider_key="minimax_api_token",
    )


async def _resolve_llm_token(
    *,
    env_keys: tuple[str, ...],
    knowledge_root: Path,
    bw_label: str,
    manifest_key: str,
    default_bw_label: str,
    bws_project_name: str,
    bws_secret_key_env: str,
    bws_secret_key: str,
    bws_secret_id_env: str,
    bw_secret_id_env: str,
    bitwarden_provider_key: str,
) -> str | None:
    for env_key in env_keys:
        direct = os.environ.get(env_key, "").strip()
        if direct:
            return direct

    bws_value = await _resolve_from_bsm(
        project_name=os.environ.get("BWS_PROJECT_NAME", bws_project_name).strip(),
        project_id=os.environ.get("BWS_PROJECT_ID", "").strip(),
        secret_key=os.environ.get(bws_secret_key_env, bws_secret_key).strip(),
        secret_id=os.environ.get(bws_secret_id_env, "").strip(),
    )
    if bws_value:
        return bws_value

    secret_id = os.environ.get(bw_secret_id_env, "").strip()
    if secret_id:
        provider = BitwardenSecretProvider({bitwarden_provider_key: secret_id})
        return (await provider.resolve(bitwarden_provider_key)).resolve()

    manifest_label = _manifest_label_for_key(knowledge_root, manifest_key)
    label = bw_label or manifest_label or default_bw_label
    return await _resolve_from_bw_vault(knowledge_root, label)


async def _resolve_from_bsm(
    *,
    project_name: str,
    project_id: str,
    secret_key: str,
    secret_id: str,
) -> str | None:
    token = os.environ.get("BWS_ACCESS_TOKEN", "").strip()
    if not token:
        return None

    bws = shutil.which("bws")
    if bws is None:
        return None

    env = {**os.environ, "BWS_ACCESS_TOKEN": token}

    if secret_id:
        return await _bws_secret_value(bws, secret_id, env)

    resolved_project_id = project_id
    if not resolved_project_id and project_name:
        projects = await _bws_json(bws, ["project", "list"], env)
        if projects is None:
            return None
        for project in _iter_bws_records(projects):
            if project.get("name") == project_name:
                resolved_project_id = str(project.get("id", ""))
                break

    secrets = await _bws_json(bws, ["secret", "list"], env)
    if secrets is None:
        return None

    for item in _iter_bws_records(secrets):
        if item.get("key") != secret_key:
            continue
        if resolved_project_id and item.get("projectId") != resolved_project_id:
            continue
        item_id = str(item.get("id", ""))
        if not item_id:
            continue
        return await _bws_secret_value(bws, item_id, env)
    return None


async def _bws_secret_value(bws: str, secret_id: str, env: dict[str, str]) -> str | None:
    data = await _bws_json(bws, ["secret", "get", secret_id], env)
    if not isinstance(data, dict):
        return None
    value = data.get("value")
    return str(value).strip() if value else None


async def _bws_json(bws: str, args: list[str], env: dict[str, str]) -> object | None:
    process = await asyncio.create_subprocess_exec(
        bws,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )
    stdout, _stderr = await process.communicate()
    if process.returncode != 0:
        return None
    try:
        parsed: object = json.loads(stdout.decode())
        return parsed
    except json.JSONDecodeError:
        return None


def _iter_bws_records(data: object) -> list[dict[str, object]]:
    if not isinstance(data, list):
        return []
    records: list[dict[str, object]] = []
    for item in data:
        if isinstance(item, dict):
            records.append(item)
    return records


def _manifest_label_for_key(knowledge_root: Path, key: str) -> str | None:
    config_path = knowledge_root / ".secrets" / "config.json"
    if not config_path.is_file():
        return None
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    secrets = data.get("secrets")
    if isinstance(secrets, dict):
        label = secrets.get(key)
        if isinstance(label, str) and label.strip():
            return label.strip()
    return None


async def _resolve_from_bw_vault(knowledge_root: Path, label: str) -> str | None:
    lib = knowledge_root / "01-Base-Point" / "tools" / "bitwarden" / "lib.sh"
    if not lib.is_file():
        return None

    script = f'set -euo pipefail; source "{lib}"; bw_load_session; bw_get_secret "{label}"'
    process = await asyncio.create_subprocess_exec(
        "/bin/bash",
        "-lc",
        script,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _stderr = await process.communicate()
    if process.returncode != 0:
        return None
    value = stdout.decode().strip()
    return value or None
