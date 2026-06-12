from datetime import datetime, timezone
import uuid
from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimeStampedModel, UUIDPrimaryKey


class SSHUser(Base, UUIDPrimaryKey, TimeStampedModel):
    __tablename__ = "ssh_users"

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    
    server_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("servers.id", ondelete="CASCADE"), nullable=False)
    reseller_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("resellers.id", ondelete="SET NULL"), nullable=True)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)  # ACTIVE, SUSPENDED, EXPIRED, DISABLED
    expiration_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    traffic_limit_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)  # 0 means unlimited
    traffic_used_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    
    connection_limit: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    server: Mapped["Server"] = relationship(back_populates="users")
    reseller: Mapped["Reseller | None"] = relationship(back_populates="users")
    created_by: Mapped["Admin | None"] = relationship(foreign_keys=[created_by_id])
    
    login_history: Mapped[list["LoginHistory"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    traffic_records: Mapped[list["TrafficRecord"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class LoginHistory(Base, UUIDPrimaryKey):
    __tablename__ = "login_histories"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ssh_users.id", ondelete="CASCADE"), nullable=False)
    server_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("servers.id", ondelete="CASCADE"), nullable=False)
    
    source_ip: Mapped[str] = mapped_column(String(45), nullable=False)
    login_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    logout_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped[SSHUser] = relationship(back_populates="login_history")
    server: Mapped["Server"] = relationship(back_populates="login_history")
