from datetime import datetime, timezone
import uuid
from sqlalchemy import Boolean, DateTime, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimeStampedModel, UUIDPrimaryKey


class Admin(Base, UUIDPrimaryKey, TimeStampedModel):
    __tablename__ = "admins"

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="RESELLER", nullable=False)  # SUPER_ADMIN, ADMIN, SUPPORT, RESELLER
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # 2FA
    totp_secret: Mapped[str | None] = mapped_column(String(32), nullable=True)
    totp_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Granular permission overrides (List of Permission strings)
    permissions: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)

    # Relationships
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="admin", cascade="all, delete-orphan")
    reseller_profile: Mapped["Reseller | None"] = relationship(back_populates="admin", uselist=False, cascade="all, delete-orphan")


class AuditLog(Base, UUIDPrimaryKey):
    __tablename__ = "audit_logs"

    admin_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "CREATE_USER", "DELETE_SERVER"
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "USER", "SERVER"
    resource_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    admin: Mapped[Admin | None] = relationship(back_populates="audit_logs")
