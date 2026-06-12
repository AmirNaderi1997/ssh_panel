import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ServerGroupBase(BaseModel):
    name: str
    description: str | None = None


class ServerGroupCreate(ServerGroupBase):
    pass


class ServerGroupResponse(ServerGroupBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ServerBase(BaseModel):
    name: str
    hostname: str
    ip_address: str
    ssh_port: int = 22
    auth_method: str = "PASSWORD"  # PASSWORD, SSH_KEY
    root_username: str = "root"
    country: str | None = None
    provider: str | None = None
    notes: str | None = None
    status: str = "OFFLINE"
    group_id: uuid.UUID | None = None


class ServerCreate(ServerBase):
    root_password: str | None = None
    ssh_key: str | None = None


class ServerUpdate(BaseModel):
    name: str | None = None
    hostname: str | None = None
    ip_address: str | None = None
    ssh_port: int | None = None
    auth_method: str | None = None
    root_username: str | None = None
    root_password: str | None = None
    ssh_key: str | None = None
    country: str | None = None
    provider: str | None = None
    notes: str | None = None
    status: str | None = None
    group_id: uuid.UUID | None = None


class ServerResponse(ServerBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    last_health_check: datetime | None = None
    created_at: datetime
    updated_at: datetime
