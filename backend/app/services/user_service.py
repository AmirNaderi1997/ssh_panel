import uuid
import secrets
import string
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.exceptions import EntityNotFoundException, BusinessRuleException
from backend.app.core.security import encrypt_field, decrypt_field
from backend.app.models.admin import Admin
from backend.app.models.user import SSHUser
from backend.app.repositories.user_repo import UserRepository
from backend.app.repositories.server_repo import ServerRepository
from backend.app.schemas.user import SSHUserCreate, SSHUserUpdate, SSHUserBulkCreate
from backend.app.services.ssh_service import SSHService


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.server_repo = ServerRepository(db)
        self.ssh_service = SSHService()

    def _generate_random_password(self, length: int = 12) -> str:
        """Generate a secure random password."""
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    async def create_user(self, user_in: SSHUserCreate, creator: Admin) -> SSHUser:
        """Create user in DB and execute user creation on the remote server."""
        # Check uniqueness
        existing = await self.user_repo.get_by_username(user_in.username)
        if existing:
            raise BusinessRuleException(f"Username '{user_in.username}' is already taken")

        # Get server
        server = await self.server_repo.get(user_in.server_id)
        if not server:
            raise EntityNotFoundException("Server", user_in.server_id)

        # Encrypt password for DB storage
        encrypted_pw = encrypt_field(user_in.password)

        db_obj = SSHUser(
            username=user_in.username,
            password_encrypted=encrypted_pw,
            server_id=user_in.server_id,
            reseller_id=user_in.reseller_id,
            created_by_id=creator.id,
            status="ACTIVE",
            expiration_date=user_in.expiration_date,
            traffic_limit_bytes=user_in.traffic_limit_bytes,
            connection_limit=user_in.connection_limit,
            notes=user_in.notes,
        )

        # Create user on remote linux server
        await self.ssh_service.create_linux_user(
            server=server,
            username=user_in.username,
            password=user_in.password,
            expiry=user_in.expiration_date,
        )

        self.db.add(db_obj)
        await self.db.flush()
        return db_obj

    async def update_user(self, user_id: uuid.UUID, user_in: SSHUserUpdate) -> SSHUser:
        """Update user info, applying changes to remote servers as needed."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise EntityNotFoundException("SSHUser", user_id)

        server = await self.server_repo.get(user.server_id)
        if not server:
            raise EntityNotFoundException("Server", user.server_id)

        update_data = user_in.model_dump(exclude_unset=True)

        # 1. Handle password change
        if "password" in update_data:
            new_pw = update_data.pop("password")
            if new_pw:
                # Update on remote server
                await self.ssh_service.change_password(server, user.username, new_pw)
                # Encrypt and update in DB
                update_data["password_encrypted"] = encrypt_field(new_pw)

        # 2. Handle expiration date change
        if "expiration_date" in update_data:
            new_expiry = update_data["expiration_date"]
            if new_expiry:
                await self.ssh_service.set_expiration(server, user.username, new_expiry)

        # 3. Handle status change directly
        if "status" in update_data:
            new_status = update_data["status"]
            if new_status == "SUSPENDED" and user.status != "SUSPENDED":
                await self.ssh_service.lock_user(server, user.username)
            elif new_status == "ACTIVE" and user.status == "SUSPENDED":
                await self.ssh_service.unlock_user(server, user.username)

        # 4. Handle moving server
        if "server_id" in update_data:
            new_server_id = update_data["server_id"]
            if new_server_id and new_server_id != user.server_id:
                new_server = await self.server_repo.get(new_server_id)
                if not new_server:
                    raise EntityNotFoundException("Server", new_server_id)

                # Delete from old server
                await self.ssh_service.delete_linux_user(server, user.username)

                # Create on new server
                clear_pw = decrypt_field(user.password_encrypted)
                await self.ssh_service.create_linux_user(
                    server=new_server,
                    username=user.username,
                    password=clear_pw,
                    expiry=user.expiration_date,
                )

        return await self.user_repo.update(user, update_data)

    async def suspend_user(self, user_id: uuid.UUID) -> SSHUser:
        """Suspend an SSH user, locking their system account."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise EntityNotFoundException("SSHUser", user_id)
        
        if user.status != "SUSPENDED":
            server = await self.server_repo.get(user.server_id)
            if server:
                await self.ssh_service.lock_user(server, user.username)
            user.status = "SUSPENDED"
            self.db.add(user)
            await self.db.flush()
        return user

    async def activate_user(self, user_id: uuid.UUID) -> SSHUser:
        """Activate a suspended SSH user, unlocking their system account."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise EntityNotFoundException("SSHUser", user_id)
        
        if user.status == "SUSPENDED":
            server = await self.server_repo.get(user.server_id)
            if server:
                await self.ssh_service.unlock_user(server, user.username)
            user.status = "ACTIVE"
            self.db.add(user)
            await self.db.flush()
        return user

    async def delete_user(self, user_id: uuid.UUID) -> None:
        """Delete user account both locally from DB and from remote server."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise EntityNotFoundException("SSHUser", user_id)

        server = await self.server_repo.get(user.server_id)
        if server:
            try:
                await self.ssh_service.delete_linux_user(server, user.username)
            except Exception:
                # Logging error but proceeding to ensure local record cleanups are not blocked
                pass

        await self.user_repo.remove(user_id)

    async def bulk_create_users(self, bulk_in: SSHUserBulkCreate, creator: Admin) -> list[SSHUser]:
        """Perform bulk SSH user creation."""
        server = await self.server_repo.get(bulk_in.server_id)
        if not server:
            raise EntityNotFoundException("Server", bulk_in.server_id)

        created_users = []
        for i in range(1, bulk_in.count + 1):
            # Username format: prefix + index
            username = f"{bulk_in.prefix}{i}"
            
            # Generate or use password
            password = bulk_in.password if bulk_in.password else self._generate_random_password()
            
            user_create_data = SSHUserCreate(
                username=username,
                password=password,
                server_id=bulk_in.server_id,
                reseller_id=bulk_in.notes,  # Notes field used as temp mapping or simply from form
                expiration_date=bulk_in.expiration_date,
                traffic_limit_bytes=bulk_in.traffic_limit_bytes,
                connection_limit=bulk_in.connection_limit,
                notes=bulk_in.notes
            )
            
            try:
                user = await self.create_user(user_create_data, creator)
                created_users.append(user)
            except Exception:
                # Skip errors to allow bulk creation of remaining users
                continue

        return created_users
