from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimeStampedModel, UUIDPrimaryKey

# Association table for reseller access to servers
reseller_servers = Table(
    "reseller_servers",
    Base.metadata,
    Column("reseller_id", ForeignKey("resellers.id", ondelete="CASCADE"), primary_key=True),
    Column("server_id", ForeignKey("servers.id", ondelete="CASCADE"), primary_key=True),
)


class ServerGroup(Base, UUIDPrimaryKey, TimeStampedModel):
    __tablename__ = "server_groups"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    servers: Mapped[list["Server"]] = relationship(back_populates="group")


class Server(Base, UUIDPrimaryKey, TimeStampedModel):
    __tablename__ = "servers"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hostname: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    ssh_port: Mapped[int] = mapped_column(Integer, default=22, nullable=False)
    auth_method: Mapped[str] = mapped_column(String(20), default="PASSWORD", nullable=False)  # PASSWORD, SSH_KEY
    root_username: Mapped[str] = mapped_column(String(50), default="root", nullable=False)
    root_password_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    ssh_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str | None] = mapped_column(String(50), nullable=True)
    provider: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="OFFLINE", nullable=False)  # ONLINE, OFFLINE, MAINTENANCE
    agent_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_health_check: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    group_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("server_groups.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    group: Mapped[ServerGroup | None] = relationship(back_populates="servers")
    users: Mapped[list["SSHUser"]] = relationship(back_populates="server", cascade="all, delete-orphan")
    resellers: Mapped[list["Reseller"]] = relationship(
        secondary=reseller_servers, back_populates="assigned_servers"
    )
    domains: Mapped[list["Domain"]] = relationship(back_populates="server", cascade="all, delete-orphan")
    login_history: Mapped[list["LoginHistory"]] = relationship(back_populates="server", cascade="all, delete-orphan")


# We also need to add the assigned_servers relationship in Reseller.
# Let's do that by importing/updating Reseller model's relationships if needed.
# Since python imports might be circular, we define secondary relationships using string names.
