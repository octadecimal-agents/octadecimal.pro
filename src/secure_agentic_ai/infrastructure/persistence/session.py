import os

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

DEFAULT_DATABASE_URL = "sqlite+aiosqlite:///./data/dev.db"


def create_engine(database_url: str | None = None) -> AsyncEngine:
    url = database_url or os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    return create_async_engine(url, echo=False)


def create_session_factory(engine: AsyncEngine | None = None) -> async_sessionmaker[AsyncSession]:
    if engine is None:
        engine = create_engine()
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
