from decimal import Decimal
import uuid
from sqlalchemy import ForeignKey, Numeric, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimeStampedModel, UUIDPrimaryKey


class Reseller(Base, UUIDPrimaryKey, TimeStampedModel):
    __tablename__ = "resellers"

    admin_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("admins.id", ondelete="CASCADE"), unique=True, nullable=False)
    credits: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    max_users: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)  # ACTIVE, SUSPENDED

    # Relationships
    admin: Mapped["Admin"] = relationship(back_populates="reseller_profile")
    users: Mapped[list["SSHUser"]] = relationship(back_populates="reseller", cascade="all, delete-orphan")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="reseller", cascade="all, delete-orphan")
    assigned_servers: Mapped[list["Server"]] = relationship(
        secondary="reseller_servers", back_populates="resellers"
    )



class Transaction(Base, UUIDPrimaryKey, TimeStampedModel):
    __tablename__ = "transactions"

    reseller_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resellers.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # CREDIT, DEBIT, REFUND
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    admin_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    reseller: Mapped[Reseller] = relationship(back_populates="transactions")
