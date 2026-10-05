from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.auth import get_current_user
from app.config import settings
from app.db import get_db
from app.embeddings import _client
from app.models import Chunk
from app.rate_limit import check_rate_limit
from app.retrieval import hybrid_retrieve, retrieve_chunks
from app.schemas import AskRequest, AskResponse, SourceChunk

router = APIRouter()

SYSTEM_PROMPT="""You answer questions about banking policy documents.
Use ONLY the provided context. If the answeris not in the context,
say you don't know. Quote numeric values excatly as written."""

async def _latest_year(
    db: AsyncSession,
    user_id: str
) -> int:
    result=await db.execute(
        select(func.max(Chunk.year)).where(Chunk.user_id==user_id)
    )
    return result.scalar() or 2026

@router.post("/ask/stream")
async def ask_stream(
        req: AskRequest, 
        user_id:str=Depends(get_current_user),
        db: AsyncSession=Depends(get_db)
    ):
    year=req.year or await _latest_year(db,user_id)
    hits=await hybrid_retrieve(db, req.question, user_id, year)
    context="\n---\n".join(f"[page {c.page}] {c.text}" for c,_ in hits) or "no results"

    async def event_generator():
        stream=await _client.chat.completions.create(
            model=settings.answer_model,
            messages=[
                {"role":"system", "content":"Answer from the context only. Quote numbers exactly."},
                {"role":"user", "content": f"Context:\n{context}\n\nQuestion: {req.question}"}
            ],
            stream=True
        )
        async for chunk in stream:
            delta=chunk.choices[0].delta.content
            if delta:
                yield {"event": "token", "data": delta}
        yield {"event": "done", "data": ""}

    return EventSourceResponse(event_generator())

@router.post("/ask", response_model=AskResponse)
async def ask(
    req: AskRequest,
    user_id:str=Depends(get_current_user),
    db: AsyncSession=Depends(get_db)
) -> AskResponse:
    if not await check_rate_limit(user_id):
        raise HTTPException(status_code=429,detail="rate limit exceeded, try again shortly")

    year=req.year
    if year is None:
        result=await db.execute(
            select(func.max(Chunk.year))
            .where(Chunk.user_id==user_id)
        )
        year=result.scalar()
        if year is None:
            raise HTTPException(
                status_code=404,
                detail="no doc for this user"
            )
    hits=await retrieve_chunks(
        db,
        req.question,
        user_id,
        year
    )
    if not hits:
        raise HTTPException(
            status_code=404,
            detail=f"no doc for year {year}"
        )
    context="\n\n---\n\n".join(
        f"[page {c.page}, year {c.year}\n{c.text}]" for c, _ in hits
    )
    completion= await _client.chat.completions.create(
        model=settings.answer_model,
        messages=[
            {"role":"system", "content": SYSTEM_PROMPT},
            {"role":"user","content":f"Context:\n{context}\n\nQuestion:{req.question}"}
        ],
        temperature=0
    )
    answer=completion.choices[0].message.content or ""

    return AskResponse(
        answer=answer,
        sources=[
            SourceChunk(page=c.page,year=c.year,text=c.text[:300],score=round(s,3))
            for c,s in hits
        ]
    )