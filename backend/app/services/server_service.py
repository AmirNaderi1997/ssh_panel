import uuid
from datetime import datetime, timezone
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.exceptions import EntityNotFoundException, BusinessRuleException
from backend.app.core.security import encrypt_field
from backend.app.models.server import Server, ServerGroup
from backend.app.repositories.server_repo import ServerRepository, ServerGroupRepository
from backend.app.schemas.server import ServerCreate, ServerUpdate, ServerGroupCreate
from backend.app.services.ssh_service import SSHService


class ServerService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.server_repo = ServerRepository(db)
        self.group_repo = ServerGroupRepository(db)
        self.ssh_service = SSHService()

    async def add_server(self, server_in: ServerCreate) -> Server:
        """Add a new server, test connectivity, and store encrypted credentials."""
        # Check if server with name already exists
        existing = await self.server_repo.get_by_name(server_in.name)
        if existing:
            raise BusinessRuleException(f"Server with name '{server_in.name}' already exists")

        # Encrypt password if present
        encrypted_password = None
        if server_in.root_password:
            encrypted_password = encrypt_field(server_in.root_password)

        db_obj = Server(
            name=server_in.name,
            hostname=server_in.hostname,
            ip_address=server_in.ip_address,
            ssh_port=server_in.ssh_port,
            auth_method=server_in.auth_method,
            root_username=server_in.root_username,
            root_password_encrypted=encrypted_password,
            ssh_key=server_in.ssh_key,
            country=server_in.country,
            provider=server_in.provider,
            notes=server_in.notes,
            group_id=server_in.group_id,
            status="OFFLINE",
        )
        
        # Test connection before saving
        is_online = await self.ssh_service.check_connectivity(db_obj)
        db_obj.status = "ONLINE" if is_online else "OFFLINE"
        db_obj.last_health_check = datetime.now(timezone.utc)

        self.db.add(db_obj)
        await self.db.flush()
        return db_obj

    async def update_server(self, server_id: uuid.UUID, server_in: ServerUpdate) -> Server:
        """Update server details, re-encrypt credentials if updated."""
        server = await self.server_repo.get(server_id)
        if not server:
            raise EntityNotFoundException("Server", server_id)

        update_data = server_in.model_dump(exclude_unset=True)
        
        # Handle password encryption update
        if "root_password" in update_data:
            pw = update_data.pop("root_password")
            if pw:
                update_data["root_password_encrypted"] = encrypt_field(pw)
            else:
                update_data["root_password_encrypted"] = None

        return await self.server_repo.update(server, update_data)

    async def test_connection(self, server_id: uuid.UUID) -> bool:
        """Verify SSH connection to a server."""
        server = await self.server_repo.get(server_id)
        if not server:
            raise EntityNotFoundException("Server", server_id)

        is_online = await self.ssh_service.check_connectivity(server)
        
        # Update server status
        server.status = "ONLINE" if is_online else "OFFLINE"
        server.last_health_check = datetime.now(timezone.utc)
        self.db.add(server)
        await self.db.flush()
        
        return is_online

    async def health_check_server(self, server_id: uuid.UUID) -> dict:
        """Run system metrics check on server and update DB."""
        server = await self.server_repo.get(server_id)
        if not server:
            raise EntityNotFoundException("Server", server_id)

        stats = await self.ssh_service.get_system_stats(server)
        
        # If stats CPU percent is 0.0 and ram is 0.0, it might be offline
        is_online = not (stats["cpu_percent"] == 0.0 and stats["ram_percent"] == 0.0)
        
        server.status = "ONLINE" if is_online else "OFFLINE"
        server.last_health_check = datetime.now(timezone.utc)
        self.db.add(server)
        await self.db.flush()
        
        return stats

    # Group Management
    async def create_group(self, group_in: ServerGroupCreate) -> ServerGroup:
        existing = await self.group_repo.get_by_name(group_in.name)
        if existing:
            raise BusinessRuleException(f"Group '{group_in.name}' already exists")
        return await self.group_repo.create(group_in)

    async def delete_group(self, group_id: uuid.UUID) -> None:
        group = await self.group_repo.get(group_id)
        if not group:
            raise EntityNotFoundException("ServerGroup", group_id)
        await self.group_repo.remove(group_id)
