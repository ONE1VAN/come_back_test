import json
import os

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session", autouse=True)
def _db_env():
    with PostgresContainer("postgres:16-alpine", driver="asyncpg") as pg:
        os.environ["ENVIRONMENT"] = "test"
        os.environ["POSTGRES_HOST"] = pg.get_container_host_ip()
        os.environ["POSTGRES_PORT"] = str(pg.get_exposed_port(5432))
        os.environ["POSTGRES_USER"] = pg.username
        os.environ["POSTGRES_PASSWORD"] = pg.password
        os.environ["POSTGRES_DB"] = pg.dbname
        from app.core.config import settings

        cfg = Config("alembic.ini")
        cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
        command.upgrade(cfg, "head")
        yield


@pytest_asyncio.fixture(autouse=True)
async def _clean_db():
    from app.core.database import engine

    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE books, authors, users RESTART IDENTITY CASCADE"))
    yield


@pytest_asyncio.fixture
async def client():
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def auth_headers(client) -> dict[str, str]:
    r = await client.post(
        "/api/v1/auth/register",
        json={"username": "tester", "email": "t@t.io", "password": "password123"},
    )
    return {"Authorization": f"Bearer {r.json()['accessToken']}"}


def _json_file(rows: list[dict]) -> dict:
    return {"file": ("books.json", json.dumps(rows), "application/json")}
