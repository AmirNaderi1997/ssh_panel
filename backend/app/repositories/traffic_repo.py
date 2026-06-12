from datetime import date
import uuid
from typing import List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.traffic import TrafficRecord, TrafficSummary
from backend.app.repositories.base import BaseRepository


class TrafficRecordRepository(BaseRepository[TrafficRecord]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(TrafficRecord, db)

    async def get_by_user_and_date(self, user_id: uuid.UUID, record_date: date) -> TrafficRecord | None:
        """Retrieve traffic record for specific user and date."""
        query = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.date == record_date
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user_range(self, user_id: uuid.UUID, start: date, end: date) -> List[TrafficRecord]:
        """Retrieve traffic records for a user within a date range."""
        query = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.date >= start,
                self.model.date <= end
            )
        ).order_by(self.model.date.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())


class TrafficSummaryRepository(BaseRepository[TrafficSummary]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(TrafficSummary, db)

    async def get_by_server_and_period(
        self, server_id: uuid.UUID, period: str, period_start: date
    ) -> TrafficSummary | None:
        """Retrieve traffic summary for specific server, period, and start date."""
        query = select(self.model).where(
            and_(
                self.model.server_id == server_id,
                self.model.period == period,
                self.model.period_start == period_start
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
