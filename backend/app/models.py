from pydantic import BaseModel
from typing import Optional


class AnalyzeRequest(BaseModel):
    title: Optional[str] = ""
    description: str
    domain: Optional[str] = ""


class RuleUpdate(BaseModel):
    name: str
    pattern: str
    weight: int
    category: str
    active_flag: int


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class VerifyRequest(BaseModel):
    email: str
    code: str


class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    new_password: str
