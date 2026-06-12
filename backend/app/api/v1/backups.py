import uuid
from typing import List
from fastapi import APIRouter, Depends, status, Query
from backend.app.core.permissions import Permission, PermissionChecker
from backend.app.dependencies import DBDep, ActiveAdminDep
from backend.app.schemas.backup import BackupResponse
from backend.app.services.backup_service import BackupService

router = APIRouter(prefix="/backups", tags=["Database Backup Operations"])


@router.get(
    "",
    response_model=List[BackupResponse],
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_BACKUPS))],
)
async def list_backups(db: DBDep, skip: int = 0, limit: int = 100) -> List[BackupResponse]:
    """Retrieve list of all database backup archives."""
    backup_service = BackupService(db)
    return await backup_service.backup_repo.get_multi(skip=skip, limit=limit)


@router.post(
    "",
    response_model=BackupResponse,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_BACKUPS))],
    status_code=status.HTTP_201_CREATED,
)
async def trigger_manual_backup(
    db: DBDep,
    notes: str = Query("Manual database backup", description="Backup annotation"),
    current_admin: ActiveAdminDep = None
) -> BackupResponse:
    """Export and compress database tables into an archive."""
    backup_service = BackupService(db)
    return await backup_service.create_db_backup(notes=notes, creator_id=current_admin.id)


@router.post(
    "/{backup_id}/restore",
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_BACKUPS))],
)
async def restore_database_state(db: DBDep, backup_id: uuid.UUID):
    """Decompress archive and overwrite active database state (destructive operation)."""
    backup_service = BackupService(db)
    await backup_service.restore_db_backup(backup_id)
    return {"status": "SUCCESS", "message": "Database restore completed successfully"}


@router.delete(
    "/{backup_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_BACKUPS))],
)
async def delete_backup_file(db: DBDep, backup_id: uuid.UUID):
    """Delete a backup archive record and remove the file from filesystem storage."""
    backup_service = BackupService(db)
    await backup_service.delete_backup(backup_id)
