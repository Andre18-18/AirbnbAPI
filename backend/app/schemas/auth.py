from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class AuthUserRead(BaseModel):
    id: UUID
    email: EmailStr
    active: bool


class AuthStatusResponse(BaseModel):
    authenticated: bool
    user: AuthUserRead | None = None
