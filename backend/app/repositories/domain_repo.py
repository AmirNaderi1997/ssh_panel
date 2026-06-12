import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.domain import Domain
from backend.app.repositories.base import BaseRepository


class DomainRepository(BaseRepository[Domain]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Domain, db)

    async def get_by_name(self, name: str) -> Domain | None:
        """Retrieve domain by name."""
        query = select(self.model).where(self.model.domain == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_server(self, server_id: uuid.UUID) -> List[Domain]:
        """Retrieve domains associated with a server."""
        query = select(self.model).where(self.model.server_id == server_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())
