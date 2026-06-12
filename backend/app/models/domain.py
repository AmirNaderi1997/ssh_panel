from datetime import datetime
import uuid
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimeStampedModel, UUIDPrimaryKey


class Domain(Base, UUIDPrimaryKey, TimeStampedModel):
    __tablename__ = "domains"

    domain: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    type: Mapped[str] = mapped_column(String(20), default="ROOT", nullable=False)  # ROOT, SUBDOMAIN, WILDCARD
    
    server_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("servers.id", ondelete="SET NULL"), nullable=True)
    expiration_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    dns_status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)  # PENDING, VERIFIED, FAILED
    ssl_status: Mapped[str] = mapped_column(String(20), default="NONE", nullable=False)  # NONE, ACTIVE, EXPIRED, ERROR
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    server: Mapped["Server | None"] = relationship(back_populates="domains")
    certificates: Mapped[list["Certificate"]] = relationship(back_populates="domain", cascade="all, delete-orphan")
