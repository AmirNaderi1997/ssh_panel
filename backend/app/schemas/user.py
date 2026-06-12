import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class SSHUserBase(BaseModel):
    username: str
    server_id: uuid.UUID
    reseller_id: uuid.UUID | None = None
    status: str = "ACTIVE"
    expiration_date: datetime
    traffic_limit_bytes: int = 0
    connection_limit: int = 1
    notes: str | None = None


class SSHUserCreate(SSHUserBase):
    password: str


class SSHUserBulkCreate(BaseModel):
    prefix: str
    count: int
    password: str | None = None  # If null, generate random/same
    server_id: uuid.UUID
    expiration_date: datetime
    traffic_limit_bytes: int = 0
    connection_limit: int = 1
    notes: str | None = None


class SSHUserUpdate(BaseModel):
    password: str | None = None
    status: str | None = None
    expiration_date: datetime | None = None
    traffic_limit_bytes: int | None = None
    connection_limit: int | None = None
    notes: str | None = None
    server_id: uuid.UUID | None = None
    reseller_id: uuid.UUID | None = None


class SSHUserResponse(SSHUserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    traffic_used_bytes: int
    created_by_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


class LoginHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    server_id: uuid.UUID
    source_ip: str
    login_time: datetime
    logout_time: datetime | None = None
