import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CertificateBase(BaseModel):
    domain_id: uuid.UUID
    issuer: str
    issue_date: datetime
    expiration_date: datetime
    validation_method: str = "HTTP-01"  # HTTP-01, DNS-01, TLS-ALPN-01
    status: str = "PENDING"
    fingerprint: str | None = None
    auto_renew: bool = True
    acme_account_id: str | None = None


class CertificateCreate(CertificateBase):
    certificate_pem: str
    private_key: str
    chain_pem: str | None = None


class CertificateUpdate(BaseModel):
    issuer: str | None = None
    issue_date: datetime | None = None
    expiration_date: datetime | None = None
    validation_method: str | None = None
    status: str | None = None
    fingerprint: str | None = None
    auto_renew: bool | None = None
    acme_account_id: str | None = None


class CertificateResponse(CertificateBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    certificate_pem: str
    chain_pem: str | None = None
    created_at: datetime
    updated_at: datetime
