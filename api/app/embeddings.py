from openai import APIStatusError, AsyncOpenAI
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.config import settings

_client=AsyncOpenAI(api_key=settings.openai_api_key)


def _is_retryable(exc:BaseException) -> bool:
    return isinstance(exc, APIStatusError) and (exc.status_code==429 or exc.status_code >=500)

@retry(
    retry=retry_if_exception(_is_retryable),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def embed_texts(texts: list[str]) -> list[list[float]]:
    response=await _client.embeddings.create(model=settings.embed_model,input=texts)
    return [item.embedding for item in response.data]