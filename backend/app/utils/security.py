from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from fastapi import Header, HTTPException, Request, status

from app.config import get_settings

settings = get_settings()
REQUEST_BUCKETS: dict[str, deque[datetime]] = defaultdict(deque)


async def verify_admin_token(x_admin_token: str | None = Header(default=None)) -> None:
    if x_admin_token != settings.admin_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin token.")


def enforce_rate_limit(request: Request) -> None:
    now = datetime.now(timezone.utc)
    ip = request.client.host if request.client else "unknown"
    bucket = REQUEST_BUCKETS[ip]
    cutoff = now - timedelta(seconds=settings.request_rate_window_seconds)
    while bucket and bucket[0] < cutoff:
        bucket.popleft()
    if len(bucket) >= settings.request_rate_limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded.")
    bucket.append(now)
