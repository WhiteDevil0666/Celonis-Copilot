"""
utils/logger.py
Structured logging for the Celonis AI Agent SaaS.
Logs to file + stdout with rotation, context tracking, and error alerts.
"""

import sys
import os
from loguru import logger
from datetime import datetime

# ── Log directory ─────────────────────────────────────────────────────────────
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# ── Remove default handler ────────────────────────────────────────────────────
logger.remove()

# ── Console handler (clean format) ───────────────────────────────────────────
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <white>{message}</white>",
    colorize=True,
)

# ── File handler — all logs, rotated daily ───────────────────────────────────
logger.add(
    f"{LOG_DIR}/app_{{time:YYYY-MM-DD}}.log",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="00:00",       # rotate at midnight
    retention="30 days",    # keep 30 days
    compression="zip",
    enqueue=True,           # async-safe
)

# ── Error-only file ───────────────────────────────────────────────────────────
logger.add(
    f"{LOG_DIR}/errors.log",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line}\n{message}\n",
    rotation="10 MB",
    retention="90 days",
    compression="zip",
    enqueue=True,
)


def log_query(user_id: str, query: str, model: str, tokens: int, latency_ms: float):
    """Log every AI query with structured context."""
    logger.bind(
        user_id=user_id,
        model=model,
        tokens=tokens,
        latency_ms=round(latency_ms, 2),
    ).info(f"QUERY | user={user_id} | model={model} | tokens={tokens} | {latency_ms:.0f}ms | q={query[:80]!r}")


def log_error(user_id: str, error: Exception, context: str = ""):
    """Log errors with full context."""
    logger.bind(user_id=user_id).error(
        f"ERROR | user={user_id} | ctx={context} | {type(error).__name__}: {error}"
    )


def log_rate_limit(user_id: str, endpoint: str):
    """Log rate limit hits."""
    logger.warning(f"RATE_LIMIT | user={user_id} | endpoint={endpoint}")


def log_auth(user_id: str, action: str, success: bool):
    """Log auth events."""
    level = "info" if success else "warning"
    getattr(logger, level)(f"AUTH | user={user_id} | action={action} | success={success}")


def log_rag(query: str, chunks_found: int, top_score: float):
    """Log RAG retrieval results."""
    logger.debug(f"RAG | chunks={chunks_found} | top_score={top_score:.3f} | q={query[:60]!r}")
