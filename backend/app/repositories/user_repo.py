import uuid
from datetime import datetime, timezone
from typing import List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.user import SSHUser, LoginHistory
from backend.app.repositories.base import BaseRepository


class UserRepository(BaseRepository[SSHUser]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(SSHUser, db)

    async def get_by_username(self, username: str) -> SSHUser | None:
        """Retrieve SSHUser by username."""
        query = select(self.model).where(self.model.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_server(self, server_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[SSHUser]:
        """Retrieve SSHUsers assigned to a server."""
        query = select(self.model).where(self.model.server_id == server_id).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_reseller(self, reseller_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[SSHUser]:
        """Retrieve SSHUsers created by a reseller."""
        query = select(self.model).where(self.model.reseller_id == reseller_id).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_users_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[SSHUser]:
        """Retrieve users by status."""
        query = select(self.model).where(self.model.status == status).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_expired_users(self) -> List[SSHUser]:
        """Retrieve users whose expiration date is in the past and are not yet marked EXPIRED."""
        now = datetime.now(timezone.utc)
        query = select(self.model).where(
            and_(
                self.model.expiration_date <= now,
                self.model.status != "EXPIRED"
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())


class LoginHistoryRepository(BaseRepository[LoginHistory]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(LoginHistory, db)

    async def get_active_sessions(self, skip: int = 0, limit: int = 100) -> List[LoginHistory]:
        """Retrieve active sessions (logout_time is null)."""
        query = (
            select(self.model)
            .where(self.model.logout_time == None)
            .order_by(self.model.login_time.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_active_session_by_user_and_ip(
        self, user_id: uuid.UUID, source_ip: str
    ) -> LoginHistory | None:
        """Retrieve active login session for specific user and IP."""
        query = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.source_ip == source_ip,
                self.model.logout_time == None,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
