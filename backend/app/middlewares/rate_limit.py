"""Rate limiting middleware with periodic cleanup of stale IP entries.

Uses an in-memory sliding window. Old IP entries are pruned periodically
to prevent unbounded memory growth.
"""

import logging
import time
from collections import defaultdict

from fastapi import Request, HTTPException

logger = logging.getLogger(__name__)

# Sliding window: {ip: [timestamps]}
rate_limit_store: dict[str, list[float]] = defaultdict(list)

# Last cleanup timestamp
_last_cleanup = time.time()
_CLEANUP_INTERVAL = 300  # Run cleanup every 5 minutes
_ENTRY_TTL = 120  # Remove IP entries with no activity in the last 2 minutes
_MAX_REQUESTS_PER_MINUTE = 60


def _cleanup_stale_entries():
    """Remove IP entries that haven't been seen recently."""
    global _last_cleanup
    now = time.time()
    if now - _last_cleanup < _CLEANUP_INTERVAL:
        return
    _last_cleanup = now

    stale_ips = [
        ip for ip, times in rate_limit_store.items()
        if not times or now - times[-1] > _ENTRY_TTL
    ]
    for ip in stale_ips:
        del rate_limit_store[ip]
    if stale_ips:
        logger.debug("Rate limiter pruned %d stale IP entries", len(stale_ips))


async def rate_limit_middleware(request: Request, call_next):
    # Skip rate limiting for health checks
    if request.url.path.endswith("/health"):
        return await call_next(request)

    # Behind the nginx reverse proxy, request.client.host is the nginx
    # container IP, which would make ALL users share a single rate-limit
    # bucket. nginx sets X-Real-IP to the true remote address — use it when
    # present, otherwise fall back to the direct-connection client host.
    client_ip = request.headers.get("X-Real-IP")
    if not client_ip:
        client_ip = request.client.host if request.client else "unknown"
    now = time.time()

    # Periodic cleanup
    _cleanup_stale_entries()

    # Sliding window: keep only timestamps from the last 60 seconds
    window = [t for t in rate_limit_store[client_ip] if now - t < 60]
    if len(window) >= _MAX_REQUESTS_PER_MINUTE:
        raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")
    window.append(now)
    rate_limit_store[client_ip] = window
    return await call_next(request)
