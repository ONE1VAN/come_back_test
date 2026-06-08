from fastapi import APIRouter
from sqlalchemy import text

from app.api.dependencies import DBSession

router = APIRouter()


@router.get("/")
async def health(session: DBSession) -> dict:
    await session.execute(text("SELECT 1"))
    return {"status": "ok"}
