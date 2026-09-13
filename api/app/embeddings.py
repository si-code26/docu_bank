import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

EMBED_MODEL="text-embedding-3-small"

_client=AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

async def embed_texts(texts: list[str]) -> list[list[float]]:
    response=await _client.embeddings.create(model=EMBED_MODEL,input=texts)
    return [item.embedding for item in response.data]