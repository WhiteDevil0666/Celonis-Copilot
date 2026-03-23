"""
utils/auth.py
Authentication layer using Supabase.
- Email + password sign-up / sign-in
- Session persistence in st.session_state
- User tier management (free / pro / admin)
- Falls back to API-key-only mode if Supabase is not configured

Setup:
  1. Create project at supabase.com (free tier works)
  2. Add SUPABASE_URL and SUPABASE_KEY to .streamlit/secrets.toml
"""

import streamlit as st
from utils.logger import logger, log_auth

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


# ── Internal helpers ──────────────────────────────────────────────────────────

def _get_supabase() -> "Client | None":
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    if url and key and SUPABASE_AVAILABLE:
        return create_client(url, key)
    return None


def _init_session():
    defaults = {
        "auth_user":  None,      # dict: {id, email, tier}
        "auth_token": None,
        "logged_in":  False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Public API ────────────────────────────────────────────────────────────────

def sign_up(email: str, password: str) -> tuple[bool, str]:
    """Register a new user."""
    _init_session()
    sb = _get_supabase()
    if not sb:
        return False, "Auth not configured. Use API-key mode."

    try:
        res = sb.auth.sign_up({"email": email, "password": password})
        if res.user:
            log_auth(email, "sign_up", True)
            return True, "✅ Account created! Check your email to confirm."
        return False, "Sign-up failed. Try a different email."
    except Exception as e:
        log_auth(email, "sign_up", False)
        logger.error(f"Sign-up error: {e}")
        return False, f"Error: {str(e)}"


def sign_in(email: str, password: str) -> tuple[bool, str]:
    """Sign in and populate session state."""
    _init_session()
    sb = _get_supabase()
    if not sb:
        return False, "Auth not configured. Use API-key mode."

    try:
        res = sb.auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            tier = _get_user_tier(sb, res.user.id)
            st.session_state.auth_user  = {
                "id":    res.user.id,
                "email": res.user.email,
                "tier":  tier,
            }
            st.session_state.auth_token = res.session.access_token
            st.session_state.logged_in  = True
            st.session_state.rate_limit_tier = tier   # sync with rate limiter
            log_auth(email, "sign_in", True)
            return True, f"✅ Welcome back, {email}!"
        return False, "Invalid email or password."
    except Exception as e:
        log_auth(email, "sign_in", False)
        return False, "Invalid credentials."


def sign_out():
    """Clear session."""
    _init_session()
    email = st.session_state.auth_user.get("email", "") if st.session_state.auth_user else ""
    st.session_state.auth_user  = None
    st.session_state.auth_token = None
    st.session_state.logged_in  = False
    st.session_state.messages   = []
    log_auth(email, "sign_out", True)


def is_logged_in() -> bool:
    _init_session()
    return bool(st.session_state.logged_in)


def get_current_user() -> dict | None:
    _init_session()
    return st.session_state.auth_user


def get_user_tier() -> str:
    user = get_current_user()
    return user["tier"] if user else "free"


def _get_user_tier(sb, user_id: str) -> str:
    """Fetch tier from Supabase profiles table (create this table in Supabase)."""
    try:
        res = sb.table("profiles").select("tier").eq("id", user_id).single().execute()
        return res.data.get("tier", "free") if res.data else "free"
    except Exception:
        return "free"


# ── Auth UI components ────────────────────────────────────────────────────────

def render_auth_form():
    """
    Renders sign-in / sign-up form.
    Returns True if user is authenticated after this render.
    """
    _init_session()

    if is_logged_in():
        return True

    sb_configured = bool(
        SUPABASE_AVAILABLE
        and st.secrets.get("SUPABASE_URL")
        and st.secrets.get("SUPABASE_KEY")
    )

    if not sb_configured:
        st.info("💡 **Auth not configured.** Running in API-key mode. "
                "Add `SUPABASE_URL` and `SUPABASE_KEY` to secrets for full auth.")
        # Auto-login as free user in API-key-only mode
        st.session_state.logged_in  = True
        st.session_state.auth_user  = {"id": "anon", "email": "guest", "tier": "free"}
        return True

    tab_login, tab_register = st.tabs(["🔑 Sign In", "✨ Create Account"])

    with tab_login:
        with st.form("login_form"):
            email    = st.text_input("Email", placeholder="you@company.com")
            password = st.text_input("Password", type="password")
            submit   = st.form_submit_button("Sign In", use_container_width=True)
            if submit and email and password:
                ok, msg = sign_in(email, password)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with tab_register:
        with st.form("register_form"):
            email    = st.text_input("Email", placeholder="you@company.com", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_pass",
                                      help="Minimum 8 characters")
            submit   = st.form_submit_button("Create Account", use_container_width=True)
            if submit and email and password:
                if len(password) < 8:
                    st.error("Password must be at least 8 characters.")
                else:
                    ok, msg = sign_up(email, password)
                    st.success(msg) if ok else st.error(msg)

    return False
