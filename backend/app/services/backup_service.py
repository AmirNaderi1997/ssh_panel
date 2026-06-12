import gzip
import json
import os
import uuid
from datetime import datetime, timezone
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.config import settings
from backend.app.core.exceptions import EntityNotFoundException, BusinessRuleException
from backend.app.core.logging import logger
from backend.app.models.backup import Backup
from backend.app.repositories.backup_repo import BackupRepository


class BackupService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.backup_repo = BackupRepository(db)
        # Dynamically set backup directory relative to the project root/backend directory
        self.backup_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "backups"
        )
        os.makedirs(self.backup_dir, exist_ok=True)

    async def create_db_backup(self, notes: str | None = None, creator_id: uuid.UUID | None = None) -> Backup:
        """Serialize database records to a compressed JSON archive file."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}.json.gz"
        filepath = os.path.join(self.backup_dir, filename)

        logger.info("Initializing database backup creation", file=filename)
        
        # We define a helper to serialize all models to dicts
        backup_data = {}
        
        try:
            # Let's import all models
            from backend.app.models import Admin, SSHUser, Server, Domain, Certificate
            
            # Fetch all tables data
            admins = (await self.db.execute(select(Admin))).scalars().all()
            users = (await self.db.execute(select(SSHUser))).scalars().all()
            servers = (await self.db.execute(select(Server))).scalars().all()
            domains = (await self.db.execute(select(Domain))).scalars().all()
            certs = (await self.db.execute(select(Certificate))).scalars().all()

            # Format to JSON serializable structures
            # Standard python json serializer needs strings for datetimes/UUIDs
            def serialize_list(items):
                result = []
                for item in items:
                    item_dict = {}
                    for col in item.__table__.columns:
                        val = getattr(item, col.name)
                        if isinstance(val, (datetime, timezone)):
                            item_dict[col.name] = val.isoformat()
                        elif isinstance(val, uuid.UUID):
                            item_dict[col.name] = str(val)
                        else:
                            item_dict[col.name] = val
                    result.append(item_dict)
                return result

            backup_data["admins"] = serialize_list(admins)
            backup_data["servers"] = serialize_list(servers)
            backup_data["users"] = serialize_list(users)
            backup_data["domains"] = serialize_list(domains)
            backup_data["certs"] = serialize_list(certs)

            # Write gzip file
            with gzip.open(filepath, "wt", encoding="utf-8") as f:
                json.dump(backup_data, f)

            file_size = os.path.getsize(filepath)
            
            backup = Backup(
                type="DATABASE",
                filename=filename,
                file_size=file_size,
                status="COMPLETED",
                created_by_id=creator_id,
                notes=notes
            )
            
            self.db.add(backup)
            await self.db.flush()
            
            logger.info("Database backup created successfully", file=filename, size=file_size)
            return backup
        except Exception as e:
            logger.error("Failed to create database backup", error=str(e))
            if os.path.exists(filepath):
                os.remove(filepath)
            raise BusinessRuleException(f"Backup creation failed: {str(e)}")

    async def restore_db_backup(self, backup_id: uuid.UUID) -> None:
        """Decompress archive and overwrite active database records."""
        backup = await self.backup_repo.get(backup_id)
        if not backup:
            raise EntityNotFoundException("Backup", backup_id)

        filepath = os.path.join(self.backup_dir, backup.filename)
        if not os.path.exists(filepath):
            raise BusinessRuleException(f"Backup archive file {backup.filename} not found on disk")

        logger.info("Initializing database restoration from file", file=backup.filename)
        
        try:
            with gzip.open(filepath, "rt", encoding="utf-8") as f:
                backup_data = json.load(f)

            # Let's import all models
            from backend.app.models import Admin, SSHUser, Server, Domain, Certificate
            
            # 1. Clear current tables
            await self.db.execute(delete(Certificate))
            await self.db.execute(delete(Domain))
            await self.db.execute(delete(SSHUser))
            await self.db.execute(delete(Server))
            await self.db.execute(delete(Admin))
            
            # Helper to parse dates
            def parse_val(val):
                if isinstance(val, str):
                    try:
                        return datetime.fromisoformat(val)
                    except ValueError:
                        try:
                            return uuid.UUID(val)
                        except ValueError:
                            pass
                return val

            # Helper to insert list of dicts
            async def restore_table(model_cls, data_list):
                for item_dict in data_list:
                    parsed_dict = {k: parse_val(v) for k, v in item_dict.items()}
                    # Convert primary key column to UUID object
                    if "id" in parsed_dict and isinstance(parsed_dict["id"], str):
                        parsed_dict["id"] = uuid.UUID(parsed_dict["id"])
                    
                    obj = model_cls(**parsed_dict)
                    self.db.add(obj)
                await self.db.flush()

            # Restore in correct order (dependency order)
            await restore_table(Admin, backup_data.get("admins", []))
            await restore_table(Server, backup_data.get("servers", []))
            await restore_table(SSHUser, backup_data.get("users", []))
            await restore_table(Domain, backup_data.get("domains", []))
            await restore_table(Certificate, backup_data.get("certs", []))
            
            logger.info("Database restored successfully from file", file=backup.filename)
        except Exception as e:
            logger.error("Failed to restore database from backup file", error=str(e))
            raise BusinessRuleException(f"Backup restoration failed: {str(e)}")

    async def delete_backup(self, backup_id: uuid.UUID) -> None:
        """Remove backup record and delete file from disk."""
        backup = await self.backup_repo.get(backup_id)
        if not backup:
            raise EntityNotFoundException("Backup", backup_id)

        filepath = os.path.join(self.backup_dir, backup.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            
        await self.backup_repo.remove(backup_id)
