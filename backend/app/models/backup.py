import uuid
from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, TimeStampedModel, UUIDPrimaryKey


class Backup(Base, UUIDPrimaryKey, TimeStampedModel):
    __tablename__ = "backups"

    type: Mapped[str] = mapped_column(String(20), default="DATABASE", nullable=False)  # DATABASE, CONFIG, SSL, FULL
    filename: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)  # size in bytes
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)  # PENDING, COMPLETED, FAILED
    
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)
    schedule_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    created_by: Mapped["Admin | None"] = relationship()
