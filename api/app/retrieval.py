from sqlalchemy import select, func, text as sql_text
from sqlalchemy.ext.asyncio import AsyncSession

from app.embeddings import embed_texts
from app.models import Chunk

TOP_K = 4
RRF_K=60

async def retrieve_chunks(
    db: AsyncSession,
    question: str,
    user_id: str,
    year: int
) -> list[tuple[Chunk,float]]:
    query_vector = (await embed_texts([question]))[0]
    distance=Chunk.embedding.cosine_distance(query_vector)
    stmt=(
        select(Chunk, distance.label("distance"))
        .where(
            Chunk.user_id==user_id,
            Chunk.year==year
        )
        .order_by(distance)
        .limit(TOP_K)
    )
    result=await db.execute(stmt)
    return [(row.Chunk,1.0-row.distance) for row in result.all()]


async def keyword_search(db,question,user_id,year):
    stmt=(
        select(Chunk)
        .where(
            Chunk.user_id==user_id,
            Chunk.year==year,
            Chunk.tsv.op("@@")(func.plainto_tsquery("english",question))
        )
        .order_by(
            func.ts_rank(Chunk.tsv, func.plainto_tsquery("english", question)).desc()
        )
        .limit(TOP_K)
    )
    return [row.Chunk for row in (await db.execute(stmt)).all()]

async def hybrid_retrieve(db,question,user_id,year):
    vec_task=retrieve_chunks(db,question,user_id,year)
    vec_hits=await vec_task
    kw_hits=await keyword_search(db,question,user_id,year)

    scores: dict = {}
    chunks: dict = {}
    for rank, (c, _) in enumerate(vec_hits, 1):
        scores[c.id] = scores.get(c.id,0) + 1 / (RRF_K + rank)
        chunks[c.id] = c
    for rank, c in enumerate(kw_hits, 1):
        scores[c.id]=scores.get(c.id,0) + 1 / (RRF_K+rank)
        chunks[c.id]=c

    top = sorted(scores, key=scores.get, reverse=True)[:TOP_K]
    return [(chunks[i], scores[i]) for i in top]
