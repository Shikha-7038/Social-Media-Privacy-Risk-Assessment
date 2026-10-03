"""
FILE: backend/utils/rate_limiter.py
PURPOSE: Tiny in-memory sliding-window rate limiter (per client IP).
Good enough for a single-process student project; use Redis/gateway in production.
"""
import threading
import time
from collections import defaultdict, deque


class RateLimiter:
    def __init__(self):
        self._hits = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, bucket: str, limit: int, window: int = 60):
        """Return (allowed, retry_after_seconds)."""
        now = time.monotonic()
        with self._lock:
            q = self._hits[bucket]
            while q and now - q[0] > window:
                q.popleft()
            if len(q) >= limit:
                return False, max(1, int(window - (now - q[0])))
            q.append(now)
            return True, 0

    def reset(self):
        with self._lock:
            self._hits.clear()
