"""
utils/token_counter.py
Accurate token counting using tiktoken (same tokenizer as OpenAI/Groq models).
Falls back to word-count estimate if tiktoken unavailable.
"""

import streamlit as st

try:
    import tiktoken
    _ENCODER = tiktoken.get_encoding("cl100k_base")   # works for Llama / Mistral family
    TIKTOKEN_AVAILABLE = True
except Exception:
    TIKTOKEN_AVAILABLE = False


def count_tokens(text: str) -> int:
    """Return accurate token count for a string."""
    if not text:
        return 0
    if TIKTOKEN_AVAILABLE:
        return len(_ENCODER.encode(text))
    # Fallback: ~1.3 tokens per word (reasonable approximation)
    return int(len(text.split()) * 1.3)


def count_messages_tokens(messages: list[dict]) -> int:
    """Count tokens across a list of {role, content} messages."""
    total = 0
    for msg in messages:
        total += count_tokens(msg.get("content", ""))
        total += 4  # per-message overhead (role + separators)
    total += 2      # priming tokens
    return total


def format_token_cost(tokens: int, model: str = "llama-3.3-70b") -> str:
    """
    Rough cost estimate in USD.
    Groq pricing (as of 2025): ~$0.59 per 1M tokens (input+output blended).
    """
    COST_PER_1M = 0.59
    cost = (tokens / 1_000_000) * COST_PER_1M
    if cost < 0.001:
        return f"~${cost:.5f}"
    return f"~${cost:.4f}"


# ── Session-level tracker ─────────────────────────────────────────────────────
def init_token_tracker():
    if "token_stats" not in st.session_state:
        st.session_state.token_stats = {
            "session_total":   0,
            "prompt_tokens":   0,
            "response_tokens": 0,
            "turns":           0,
        }


def record_tokens(prompt_tokens: int, response_tokens: int):
    init_token_tracker()
    st.session_state.token_stats["prompt_tokens"]   += prompt_tokens
    st.session_state.token_stats["response_tokens"] += response_tokens
    st.session_state.token_stats["session_total"]   += prompt_tokens + response_tokens
    st.session_state.token_stats["turns"]           += 1


def get_token_stats() -> dict:
    init_token_tracker()
    stats = st.session_state.token_stats.copy()
    stats["cost_estimate"] = format_token_cost(stats["session_total"])
    stats["tiktoken"]      = TIKTOKEN_AVAILABLE
    return stats
