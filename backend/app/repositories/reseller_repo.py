import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.reseller import Reseller, Transaction
from backend.app.repositories.base import BaseRepository


class ResellerRepository(BaseRepository[Reseller]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Reseller, db)

    async def get_by_admin_id(self, admin_id: uuid.UUID) -> Reseller | None:
        """Retrieve reseller by the corresponding Admin ID."""
        query = select(self.model).where(self.model.admin_id == admin_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Transaction, db)

    async def get_by_reseller(self, reseller_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """Retrieve transactions for a specific reseller."""
        query = (
            select(self.model)
            .where(self.model.reseller_id == reseller_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
