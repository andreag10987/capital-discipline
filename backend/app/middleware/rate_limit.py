"""
Rate-limiter en memoria para /auth/login y /auth/register.
Estructura: { IP → deque([timestamps]) }

NOTA: En producción multi-worker usar Redis.
Para desarrollo/single-worker esto funciona bien.
"""

import time
import threading
from collections import defaultdict, deque
from fastapi import Request, HTTPException, status

from ..config import settings


class RateLimiter:
    """Limiter genérico con ventana deslizante."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self._store: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        cutoff = now - self.window

        with self._lock:
            timestamps = self._store[key]

            # Podar timestamps fuera de la ventana
            while timestamps and timestamps[0] < cutoff:
                timestamps.popleft()

            if len(timestamps) >= self.max_requests:
                return False

            timestamps.append(now)

        return True

    def remaining(self, key: str) -> int:
        cutoff = time.time() - self.window
        with self._lock:
            timestamps = self._store.get(key, deque())
            valid = sum(1 for t in timestamps if t >= cutoff)
        return max(0, self.max_requests - valid)


# ── Instancia global ──────────────────────────────
login_limiter = RateLimiter(
    max_requests=settings.RATE_LIMIT_LOGIN_MAX,
    window_seconds=settings.RATE_LIMIT_LOGIN_WINDOW_SEC,
)


def get_client_ip(request: Request) -> str:
    """Obtiene la IP real considerando proxies (X-Forwarded-For)."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def check_rate_limit(request: Request):
    """
    Dependencia inyectable en endpoints de auth.
    Lanza 429 si se excede el límite.
    """
    ip = get_client_ip(request)

    if not login_limiter.is_allowed(ip):
        retry_after = settings.RATE_LIMIT_LOGIN_WINDOW_SEC
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "rate_limit_exceeded",
                "message": "Too many requests. Please wait before trying again.",
                "retry_after_seconds": retry_after,
            },
            headers={"Retry-After": str(retry_after)},
        )