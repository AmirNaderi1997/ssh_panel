from datetime import datetime
import uuid
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimeStampedModel, UUIDPrimaryKey


class Certificate(Base, UUIDPrimaryKey, TimeStampedModel):
    __tablename__ = "certificates"

    domain_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("domains.id", ondelete="CASCADE"), nullable=False)
    
    issuer: Mapped[str] = mapped_column(String(100), nullable=False)
    issue_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expiration_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    validation_method: Mapped[str] = mapped_column(String(20), default="HTTP-01", nullable=False)  # HTTP-01, DNS-01, TLS-ALPN-01
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)  # PENDING, ACTIVE, EXPIRED, REVOKED, ERROR
    
    fingerprint: Mapped[str | None] = mapped_column(String(100), nullable=True)
    certificate_pem: Mapped[str] = mapped_column(Text, nullable=False)
    private_key_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    chain_pem: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    acme_account_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    domain: Mapped["Domain"] = relationship(back_populates="certificates")
