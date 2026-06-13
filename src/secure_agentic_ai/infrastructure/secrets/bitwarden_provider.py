import asyncio
import json
import os

from secure_agentic_ai.domain.secrets import SecretValue


class BitwardenSecretProvider:
    def __init__(self, mapping: dict[str, str] | None = None) -> None:
        self._mapping = mapping or {}

    async def resolve(self, name: str) -> SecretValue:
        secret_id = self._mapping.get(name) or os.environ.get(f"BW_SECRET_ID_{name.upper()}")
        if secret_id is None:
            raise KeyError(f"No Bitwarden secret ID configured for: {name}")

        process = await asyncio.create_subprocess_exec(
            "bws",
            "secret",
            secret_id,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"bws failed: {stderr.decode().strip()}")

        data = json.loads(stdout.decode())
        return SecretValue(name=name, _value=data["value"])
