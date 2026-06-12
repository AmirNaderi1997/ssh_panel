from datetime import date
import uuid
from sqlalchemy import BigInteger, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.models.base import Base, UUIDPrimaryKey


class TrafficRecord(Base, UUIDPrimaryKey):
    __tablename__ = "traffic_records"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ssh_users.id", ondelete="CASCADE"), nullable=False)
    server_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("servers.id", ondelete="CASCADE"), nullable=False)
    
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    upload_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    download_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    # Relationships
    user: Mapped["SSHUser"] = relationship(back_populates="traffic_records")
    server: Mapped["Server"] = relationship()


class TrafficSummary(Base, UUIDPrimaryKey):
    __tablename__ = "traffic_summaries"

    server_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("servers.id", ondelete="CASCADE"), nullable=False)
    period: Mapped[str] = mapped_column(String(20), nullable=False)  # DAILY, MONTHLY
    period_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    total_upload: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    total_download: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    # Relationships
    server: Mapped["Server"] = relationship()
