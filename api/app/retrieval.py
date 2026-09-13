from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.embeddings import embed_texts
from app.models import Chunk

TOP_K = 4

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