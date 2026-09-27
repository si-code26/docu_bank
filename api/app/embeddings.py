import time

import pybreaker
from openai import APIStatusError, AsyncOpenAI
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.config import settings

_client=AsyncOpenAI(api_key=settings.openai_api_key)

# Circuit breaker state
_failures=0
_opened_at: float | None=None
FAIL_MAX=5
RESET_TIMEOUT=30

embedding_breaker=pybreaker.CircuitBreaker(
    fail_max=FAIL_MAX,
    reset_timeout=RESET_TIMEOUT
)

def _is_retryable(exc:BaseException) -> bool:
    return isinstance(exc, APIStatusError) and (exc.status_code==429 or exc.status_code >=500)

@embedding_breaker
@retry(
    retry=retry_if_exception(_is_retryable),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def _embed_texts_call(texts: list[str]) -> list[list[float]]:
    response=await _client.embeddings.create(model=settings.embed_model,input=texts)
    return [item.embedding for item in response.data]
    
    
async def embed_texts(texts: list[str]) -> list[list[float]]:
    global _failures, _opened_at

    if _opened_at is not None:
        if time.time() - _opened_at < RESET_TIMEOUT:
            raise RuntimeError("circuit open: embedding service unavailable")
        _opened_at=None

    try:
        result=await _embed_texts_call(texts)
        _failures=0
        return result
    except Exception:
        _failures +=1
        if _failures>=FAIL_MAX:
            _opened_at=time.time()
        raise