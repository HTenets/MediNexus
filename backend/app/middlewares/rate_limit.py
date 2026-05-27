from fastapi import Request, HTTPException
from collections import defaultdict
import time

rate_limit_store: dict[str, list[float]] = defaultdict(list)


async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    window = [t for t in rate_limit_store[client_ip] if now - t < 60]
    if len(window) > 60:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    window.append(now)
    rate_limit_store[client_ip] = window
    return await call_next(request)
