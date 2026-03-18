import secrets
import random
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
import sqlite3

from app.models import LoginRequest, RegisterRequest, VerifyRequest, ResetPasswordRequest
from app.database import get_db
from app.auth import hash_password, get_current_user, USER_SESSIONS, PENDING_CODES, RESET_CODES
from app.email import send_verification_email

router = APIRouter()


@router.post("/api/register/send-code")
def send_code(req: RegisterRequest, db: sqlite3.Connection = Depends(get_db)):
    if not req.name or not req.email or not req.password:
        raise HTTPException(status_code=400, detail="All fields required")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    if db.execute("SELECT user_id FROM users WHERE email=?", (req.email,)).fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Clear stale pending code
    PENDING_CODES.pop(req.email, None)

    code = str(random.randint(100000, 999999))
    PENDING_CODES[req.email] = {
        "code":     code,
        "name":     req.name,
        "password": hash_password(req.password),
        "expires":  datetime.now().timestamp() + 600
    }

    sent = send_verification_email(req.email, req.name, code)
    if not sent:
        return {"success": True, "message": "Code generated (email not configured)", "dev_code": code}
    return {"success": True, "message": f"Verification code sent to {req.email}"}


@router.post("/api/register/verify")
def verify_code(req: VerifyRequest, db: sqlite3.Connection = Depends(get_db)):
    pending = PENDING_CODES.get(req.email)
    if not pending:
        raise HTTPException(status_code=400, detail="No pending registration for this email")
    if datetime.now().timestamp() > pending["expires"]:
        PENDING_CODES.pop(req.email, None)
        raise HTTPException(status_code=400, detail="Verification code expired. Please register again.")
    if pending["code"] != req.code.strip():
        raise HTTPException(status_code=400, detail="Incorrect verification code")
    if db.execute("SELECT user_id FROM users WHERE email=?", (req.email,)).fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")

    cur = db.execute(
        "INSERT INTO users(name,email,password,role) VALUES(?,?,?,'JobSeeker')",
        (pending["name"], req.email, pending["password"])
    )
    db.commit()
    PENDING_CODES.pop(req.email, None)

    token = secrets.token_hex(32)
    USER_SESSIONS[token] = {"user_id": cur.lastrowid, "name": pending["name"], "email": req.email}
    return {"success": True, "token": token, "name": pending["name"], "email": req.email}


@router.post("/api/login")
def login(req: LoginRequest, db: sqlite3.Connection = Depends(get_db)):
    hashed = hash_password(req.password)
    user   = db.execute(
        "SELECT * FROM users WHERE email=? AND password=?", (req.email, hashed)
    ).fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    user  = dict(user)
    token = secrets.token_hex(32)
    USER_SESSIONS[token] = {"user_id": user["user_id"], "name": user["name"], "email": user["email"]}
    return {"success": True, "token": token, "name": user["name"], "email": user["email"]}


@router.post("/api/logout")
def logout(request: Request):
    token = request.headers.get("x-user-token")
    USER_SESSIONS.pop(token, None)
    return {"success": True}


@router.get("/api/me")
def me(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not logged in")
    return user


@router.post("/api/password-reset/send-code")
def reset_send_code(req: LoginRequest, db: sqlite3.Connection = Depends(get_db)):
    user = db.execute("SELECT * FROM users WHERE email=?", (req.email,)).fetchone()
    if not user:
        return {"success": True, "message": "If that email exists, a code has been sent"}

    RESET_CODES.pop(req.email, None)
    code = str(random.randint(100000, 999999))
    RESET_CODES[req.email] = {"code": code, "expires": datetime.now().timestamp() + 600}

    sent = send_verification_email(req.email, dict(user)["name"], code)
    if not sent:
        return {"success": True, "message": "Code generated (email not configured)", "dev_code": code}
    return {"success": True, "message": f"Reset code sent to {req.email}"}


@router.post("/api/password-reset/verify")
def reset_verify(req: ResetPasswordRequest, db: sqlite3.Connection = Depends(get_db)):
    pending = RESET_CODES.get(req.email)
    if not pending:
        raise HTTPException(status_code=400, detail="No reset request found for this email")
    if datetime.now().timestamp() > pending["expires"]:
        RESET_CODES.pop(req.email, None)
        raise HTTPException(status_code=400, detail="Reset code expired. Please request a new one.")
    if pending["code"] != req.code.strip():
        raise HTTPException(status_code=400, detail="Incorrect reset code")
    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    db.execute("UPDATE users SET password=? WHERE email=?", (hash_password(req.new_password), req.email))
    db.commit()
    RESET_CODES.pop(req.email, None)
    return {"success": True, "message": "Password reset successfully. You can now log in."}
