"""DocuBank API entry point"""

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import engine, get_db
from app.models import Base
from app.routers.ask import router as ask_router
from app.routers.upload import router as upload_router

app = FastAPI(title="DocuBank API")
app.include_router(upload_router)
app.include_router(ask_router)

@app.on_event("startup")
async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/db_check")
async def db_check(db: AsyncSession=Depends(get_db)) -> dict:
    result = await db.execute(text("SELECT 1"))
    return {"db": result.scalar()}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}