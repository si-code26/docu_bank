import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import JWTError

from app.config import settings

security=HTTPBearer()

_jwks_cache:dict|None=None

async def _get_jwks()->dict:
    global _jwks_cache
    if _jwks_cache is None:
        url=f"https://cognito-idp.{settings.aws_region}.amazonaws.com/{settings.cognito_user_pool_id}/.well-known/jwks.json"
        async with httpx.AsyncClient() as client:
            resp=await client.get(url)
            _jwks_cache=resp.json()
    return _jwks_cache

async def verify_token(token:str)->str:
    jwks=await _get_jwks()
    try:
        claims=jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=settings.cognito_client_id,
            issuer=f"https://cognito-idp.{settings.aws_region}.amazonaws.com/{settings.cognito_user_pool_id}"
        )
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}") from e
    return claims["sub"]

async def get_current_user(
    credentials:HTTPAuthorizationCredentials=Depends(security)
)->str:
    try:
        return await verify_token(credentials.credentials)
    except ValueError as e:
        raise HTTPException(status_code=401,detail=str(e)) from e