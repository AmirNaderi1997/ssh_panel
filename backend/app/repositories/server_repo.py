import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.server import Server, ServerGroup
from backend.app.repositories.base import BaseRepository


class ServerRepository(BaseRepository[Server]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Server, db)

    async def get_by_name(self, name: str) -> Server | None:
        """Retrieve server by name."""
        query = select(self.model).where(self.model.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_ip(self, ip_address: str) -> Server | None:
        """Retrieve server by IP address."""
        query = select(self.model).where(self.model.ip_address == ip_address)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_group(self, group_id: uuid.UUID) -> List[Server]:
        """Retrieve servers in a specific group."""
        query = select(self.model).where(self.model.group_id == group_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())


class ServerGroupRepository(BaseRepository[ServerGroup]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(ServerGroup, db)

    async def get_by_name(self, name: str) -> ServerGroup | None:
        """Retrieve server group by name."""
        query = select(self.model).where(self.model.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
