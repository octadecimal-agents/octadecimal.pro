import importlib.util
import os
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from secure_agentic_ai.infrastructure.persistence.models import ApprovalRequestRow, Base

ROOT = Path(__file__).resolve().parents[3]
_SEED_DEMO_PATH = ROOT / "scripts" / "seed_demo.py"


def _load_seed_demo():
    spec = importlib.util.spec_from_file_location("seed_demo", _SEED_DEMO_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
async def seed_db(tmp_path: Path) -> str:
    db_path = tmp_path / "seed-demo-test.db"
    database_url = f"sqlite+aiosqlite:///{db_path}"
    os.environ["DATABASE_URL"] = database_url
    engine = create_async_engine(database_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    yield database_url
    os.environ.pop("DATABASE_URL", None)


async def _demo_count(database_url: str) -> int:
    engine = create_async_engine(database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        result = await session.execute(select(ApprovalRequestRow).where(ApprovalRequestRow.request_id.like("demo-%")))
        count = len(result.scalars().all())
    await engine.dispose()
    return count


@pytest.mark.asyncio
async def test_seed_demo_is_idempotent_by_default(seed_db: str) -> None:
    seed_demo = _load_seed_demo()
    await seed_demo.seed()
    first_count = await _demo_count(seed_db)
    assert first_count == 3

    await seed_demo.seed()
    second_count = await _demo_count(seed_db)
    assert second_count == first_count


@pytest.mark.asyncio
async def test_seed_demo_reset_recreates_demo_rows(seed_db: str) -> None:
    seed_demo = _load_seed_demo()
    await seed_demo.seed()
    before = await _demo_count(seed_db)

    await seed_demo.seed(reset=True)
    after = await _demo_count(seed_db)
    assert before == 3
    assert after == 3
