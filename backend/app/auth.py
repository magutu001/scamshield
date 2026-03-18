import hashlib
from fastapi import HTTPException, Request
from app.config import ADMIN_TOKEN

# ── In-memory session stores ───────────────────────────────────────────────────
USER_SESSIONS = {}   # token -> {user_id, name, email}
PENDING_CODES = {}   # email -> {code, name, password, expires}
RESET_CODES   = {}   # email -> {code, expires}


def hash_password(password: str) -> str:
    """SHA-256 hash a password."""
    return hashlib.sha256(password.encode()).hexdigest()


def require_admin(request: Request):
    """Raise 401 if the request does not carry a valid admin token."""
    if request.headers.get("x-admin-token") != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


def get_current_user(request: Request):
    """Return the logged-in user dict from session, or None for guests."""
    token = request.headers.get("x-user-token")
    if token and token in USER_SESSIONS:
        return USER_SESSIONS[token]
    return None
