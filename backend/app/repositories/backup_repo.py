from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.backup import Backup
from backend.app.repositories.base import BaseRepository


class BackupRepository(BaseRepository[Backup]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Backup, db)

    async def get_by_filename(self, filename: str) -> Backup | None:
        """Retrieve backup record by filename."""
        query = select(self.model).where(self.model.filename == filename)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_latest_backups(self, limit: int = 10) -> list[Backup]:
        """Retrieve latest backup records."""
        query = select(self.model).order_by(self.model.created_at.desc()).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
