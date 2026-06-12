import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DomainBase(BaseModel):
    domain: str
    type: str = "ROOT"  # ROOT, SUBDOMAIN, WILDCARD
    server_id: uuid.UUID | None = None
    expiration_date: datetime | None = None
    dns_status: str = "PENDING"
    ssl_status: str = "NONE"
    notes: str | None = None


class DomainCreate(DomainBase):
    pass


class DomainUpdate(BaseModel):
    domain: str | None = None
    type: str | None = None
    server_id: uuid.UUID | None = None
    expiration_date: datetime | None = None
    dns_status: str | None = None
    ssl_status: str | None = None
    notes: str | None = None


class DomainResponse(DomainBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
