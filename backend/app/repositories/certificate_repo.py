import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.certificate import Certificate
from backend.app.repositories.base import BaseRepository


class CertificateRepository(BaseRepository[Certificate]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Certificate, db)

    async def get_by_domain(self, domain_id: uuid.UUID) -> List[Certificate]:
        """Retrieve certificates for a specific domain."""
        query = select(self.model).where(self.model.domain_id == domain_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_active_certificates(self) -> List[Certificate]:
        """Retrieve active certificates."""
        query = select(self.model).where(self.model.status == "ACTIVE")
        result = await self.db.execute(query)
        return list(result.scalars().all())
