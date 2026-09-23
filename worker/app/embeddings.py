from openai import AsyncOpenAI

from app.config import settings

_client=AsyncOpenAI(api_key=settings.openai_api_key)

async def embed_texts(texts: list[str]) -> list[list[float]]:
    response = await _client.embeddings.create(
        model=settings.embed_model,
        input=texts
    )
    return [item.embedding for item in response.data]