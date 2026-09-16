import pytest
import pytest_asyncio
from backend.app.database import engine, Base
from backend.app.main import _sync_migrate_db

@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_sync_migrate_db)
    yield
