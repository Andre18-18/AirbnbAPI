from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, status


_attempts: dict[str, deque[datetime]] = defaultdict(deque)


def rate_limit(request: Request, bucket: str, limit: int, window_seconds: int) -> None:
    client_ip = request.client.host if request.client else "unknown"
    key = f"{bucket}:{client_ip}"
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(seconds=window_seconds)
    attempts = _attempts[key]
    while attempts and attempts[0] < window_start:
        attempts.popleft()
    if len(attempts) >= limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")
    attempts.append(now)
