"""
utils/rate_limiter.py
Sliding-window rate limiter stored in Streamlit session state.
No Redis needed for single-server deploy — upgrade to Redis for multi-instance.
"""

import time
import streamlit as st
from collections import deque
from utils.logger import log_rate_limit


# ── Config ────────────────────────────────────────────────────────────────────
RATE_LIMITS = {
    "free":    {"requests": 10,  "window_seconds": 3600},   # 10 req / hour
    "pro":     {"requests": 100, "window_seconds": 3600},   # 100 req / hour
    "admin":   {"requests": 999, "window_seconds": 3600},   # unlimited effectively
}

# Hard global limit per session (prevents single-session abuse regardless of tier)
SESSION_HARD_LIMIT = {"requests": 30, "window_seconds": 3600}


class RateLimiter:
    """
    Sliding window rate limiter.
    Stores timestamps of recent requests in a deque.
    """

    def __init__(self):
        if "rate_limit_timestamps" not in st.session_state:
            st.session_state.rate_limit_timestamps = deque()
        if "rate_limit_tier" not in st.session_state:
            st.session_state.rate_limit_tier = "free"

    def _clean_window(self, timestamps: deque, window_seconds: int) -> deque:
        """Remove timestamps older than the window."""
        cutoff = time.time() - window_seconds
        while timestamps and timestamps[0] < cutoff:
            timestamps.popleft()
        return timestamps

    def check(self, user_id: str = "anonymous") -> tuple[bool, str, int]:
        """
        Check if request is allowed.
        Returns: (allowed: bool, message: str, retry_after_seconds: int)
        """
        tier      = st.session_state.get("rate_limit_tier", "free")
        limit_cfg = RATE_LIMITS.get(tier, RATE_LIMITS["free"])
        timestamps = st.session_state.rate_limit_timestamps

        # Clean old entries
        self._clean_window(timestamps, limit_cfg["window_seconds"])

        current_count = len(timestamps)

        if current_count >= limit_cfg["requests"]:
            oldest       = timestamps[0]
            retry_after  = int(oldest + limit_cfg["window_seconds"] - time.time()) + 1
            log_rate_limit(user_id, "chat_query")
            return (
                False,
                f"⏳ Rate limit reached for **{tier}** plan "
                f"({limit_cfg['requests']} requests/hour). "
                f"Try again in **{retry_after // 60}m {retry_after % 60}s**.",
                retry_after,
            )

        # Record this request
        timestamps.append(time.time())
        st.session_state.rate_limit_timestamps = timestamps

        remaining = limit_cfg["requests"] - len(timestamps)
        return True, "", remaining

    def get_usage(self) -> dict:
        """Return current usage stats for display."""
        tier      = st.session_state.get("rate_limit_tier", "free")
        limit_cfg = RATE_LIMITS.get(tier, RATE_LIMITS["free"])
        timestamps = st.session_state.get("rate_limit_timestamps", deque())

        self._clean_window(timestamps, limit_cfg["window_seconds"])
        used = len(timestamps)

        return {
            "tier":       tier,
            "used":       used,
            "limit":      limit_cfg["requests"],
            "remaining":  limit_cfg["requests"] - used,
            "window_h":   limit_cfg["window_seconds"] // 3600,
            "pct":        int((used / limit_cfg["requests"]) * 100),
        }

    def set_tier(self, tier: str):
        """Upgrade/downgrade user tier."""
        if tier in RATE_LIMITS:
            st.session_state.rate_limit_tier = tier


# ── Singleton ─────────────────────────────────────────────────────────────────
def get_rate_limiter() -> RateLimiter:
    if "rate_limiter" not in st.session_state:
        st.session_state.rate_limiter = RateLimiter()
    return st.session_state.rate_limiter
