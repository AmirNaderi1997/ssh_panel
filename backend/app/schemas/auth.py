import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str | None = None
    type: str | None = None
    exp: int | None = None


class LoginRequest(BaseModel):
    username: str
    password: str
    totp_code: str | None = None


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class Setup2FAResponse(BaseModel):
    secret: str
    qr_code_uri: str


class Verify2FARequest(BaseModel):
    code: str


class AdminBase(BaseModel):
    username: str
    email: EmailStr
    role: str
    is_active: bool = True
    permissions: list[str] | None = []


class AdminCreate(AdminBase):
    password: str


class AdminUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: str | None = None
    is_active: bool | None = None
    permissions: list[str] | None = None


class AdminResponse(AdminBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    totp_enabled: bool
    last_login: datetime | None = None
    created_at: datetime
    updated_at: datetime
