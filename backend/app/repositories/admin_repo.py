import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.admin import Admin, AuditLog
from backend.app.repositories.base import BaseRepository


class AdminRepository(BaseRepository[Admin]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Admin, db)

    async def get_by_username(self, username: str) -> Admin | None:
        """Retrieve an admin by username."""
        query = select(self.model).where(self.model.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Admin | None:
        """Retrieve an admin by email."""
        query = select(self.model).where(self.model.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(AuditLog, db)

    async def get_by_admin(self, admin_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Retrieve audit logs associated with an admin."""
        query = (
            select(self.model)
            .where(self.model.admin_id == admin_id)
            .order_by(self.model.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all_logs(self, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Retrieve all audit logs ordered by timestamp descending."""
        query = select(self.model).order_by(self.model.timestamp.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
