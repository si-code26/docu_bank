from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.embeddings import _client
from app.models import Chunk
from app.retrieval import retrieve_chunks
from app.schemas import AskRequest, AskResponse, SourceChunk

router = APIRouter()

ANSWER_MODEL="gpt-4o-mini"
SYSTEM_PROMPT="""You answer questions about banking policy documents.
Use ONLY the provided context. If the answeris not in the context,
say you don't know. Quote numeric values excatly as written."""

@router.post("/ask", response_model=AskResponse)
async def ask(
    req: AskRequest,
    db: AsyncSession=Depends(get_db)
) -> AskResponse:
    year=req.year
    if year is None:
        result=await db.execute(
            select(func.max(Chunk.year))
            .where(Chunk.user_id==req.user_id)
        )
        year=result=result.scalar()
        if year is None:
            raise HTTPException(
                status_code=404,
                detail="no doc for this user"
            )
    hits=await retrieve_chunks(
        db,
        req.question,
        req.user_id,
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
        model=ANSWER_MODEL,
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