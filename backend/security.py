import os
import logging
import re
from fastapi import HTTPException, Security, Request
from fastapi.security import APIKeyHeader

logger = logging.getLogger(__name__)

API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

MAX_QUERY_LENGTH = 500
# Block obvious SQL/script injection patterns
_BLOCKED = re.compile(
    r"(--|;|\bdrop\b|\bdelete\b|\binsert\b|\bupdate\b|\bexec\b|<script|javascript:)",
    re.IGNORECASE,
)


def verify_api_key(key: str = Security(api_key_header)):
    """
    If API_KEY env var is set, all requests must supply a matching X-API-Key header.
    If API_KEY is not configured (dev mode), auth is skipped.
    """
    if not API_KEY:
        return  # dev / local mode — no key required
    if key != API_KEY:
        logger.warning("Rejected request — invalid or missing API key")
        raise HTTPException(status_code=403, detail="Invalid or missing API key")


def validate_query(query: str) -> str:
    query = query.strip()
    if not query:
        raise HTTPException(status_code=422, detail="Query must not be empty")
    if len(query) > MAX_QUERY_LENGTH:
        raise HTTPException(
            status_code=422,
            detail=f"Query too long ({len(query)} chars). Maximum is {MAX_QUERY_LENGTH}.",
        )
    if _BLOCKED.search(query):
        logger.warning("Rejected query — blocked pattern detected: %s", query[:80])
        raise HTTPException(status_code=422, detail="Query contains disallowed content")
    return query


async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
