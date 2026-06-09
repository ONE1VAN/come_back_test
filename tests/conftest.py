import os

import pytest
import pytest_asyncio


@pytest.fixture(scope="session", autouse=True)
def _db_env():
    os.environ.setdefault("TESTCONTAINERS_RYUK_DISABLED", "true")
    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("postgres:16-alpine", driver="asyncpg") as pg:
        os.environ["ENVIRONMENT"] = "test"
        os.environ["POSTGRES_HOST"] = pg.get_container_host_ip()
        os.environ["POSTGRES_PORT"] = str(pg.get_exposed_port(5432))
        os.environ["POSTGRES_USER"] = pg.username
        os.environ["POSTGRES_PASSWORD"] = pg.password
        os.environ["POSTGRES_DB"] = pg.dbname

        from alembic import command
        from alembic.config import Config

        from app.core.config import settings

        cfg = Config("alembic.ini")
        cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
        command.upgrade(cfg, "head")
        yield


@pytest_asyncio.fixture
async def client():
    from httpx import ASGITransport, AsyncClient
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy.pool import NullPool

    from app.core.config import settings
    from app.core.database import get_session
    from app.main import app

    test_engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
    test_maker = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)

    async def _override_get_session():
        async with test_maker() as session:
            yield session

    app.dependency_overrides[get_session] = _override_get_session

    async with test_engine.begin() as conn:
        await conn.execute(text("TRUNCATE books, authors, users RESTART IDENTITY CASCADE"))

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
    await test_engine.dispose()


@pytest_asyncio.fixture
async def auth_headers(client) -> dict[str, str]:
    r = await client.post(
        "/api/v1/auth/register",
        json={"username": "tester", "email": "t@t.io", "password": "password123"},
    )
    return {"Authorization": f"Bearer {r.json()['accessToken']}"}
