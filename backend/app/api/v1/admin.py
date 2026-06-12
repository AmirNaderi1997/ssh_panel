import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from backend.app.core.exceptions import EntityNotFoundException, PermissionDeniedException, BusinessRuleException
from backend.app.core.permissions import Permission, PermissionChecker
from backend.app.dependencies import DBDep, ActiveAdminDep
from backend.app.repositories.admin_repo import AdminRepository, AuditLogRepository
from backend.app.schemas.auth import AdminCreate, AdminResponse, AdminUpdate
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/admin", tags=["Admin Management"])


@router.get(
    "/admins",
    response_model=List[AdminResponse],
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_ADMINS))],
)
async def list_admins(db: DBDep, skip: int = 0, limit: int = 100) -> List[AdminResponse]:
    """Retrieve all admin profiles. Requires MANAGE_ADMINS permission."""
    admin_repo = AdminRepository(db)
    return await admin_repo.get_multi(skip=skip, limit=limit)


@router.post(
    "/admins",
    response_model=AdminResponse,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_ADMINS))],
    status_code=status.HTTP_201_CREATED,
)
async def create_admin(db: DBDep, admin_in: AdminCreate) -> AdminResponse:
    """Create a new admin user. Requires MANAGE_ADMINS permission."""
    auth_service = AuthService(db)
    return await auth_service.register_admin(admin_in)


@router.put(
    "/admins/{admin_id}",
    response_model=AdminResponse,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_ADMINS))],
)
async def update_admin(
    db: DBDep,
    admin_id: uuid.UUID,
    admin_in: AdminUpdate,
) -> AdminResponse:
    """Update an existing admin profile. Requires MANAGE_ADMINS permission."""
    admin_repo = AdminRepository(db)
    admin = await admin_repo.get(admin_id)
    if not admin:
        raise EntityNotFoundException("Admin", admin_id)
        
    if admin_in.password:
        from backend.app.core.security import hash_password
        admin.password_hash = hash_password(admin_in.password)
        
    update_data = admin_in.model_dump(exclude={"password"}, exclude_unset=True)
    return await admin_repo.update(admin, update_data)


@router.delete(
    "/admins/{admin_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_ADMINS))],
)
async def delete_admin(db: DBDep, admin_id: uuid.UUID, current_admin: ActiveAdminDep):
    """Delete an admin profile. Cannot delete self. Requires MANAGE_ADMINS."""
    if current_admin.id == admin_id:
        raise BusinessRuleException("Cannot delete your own admin account")
        
    admin_repo = AdminRepository(db)
    admin = await admin_repo.get(admin_id)
    if not admin:
        raise EntityNotFoundException("Admin", admin_id)
        
    await admin_repo.remove(admin_id)


@router.get(
    "/audit-logs",
    dependencies=[Depends(PermissionChecker(Permission.VIEW_AUDIT))],
)
async def get_audit_logs(db: DBDep, skip: int = 0, limit: int = 100):
    """Retrieve all audit logs. Requires VIEW_AUDIT permission."""
    audit_repo = AuditLogRepository(db)
    return await audit_repo.get_all_logs(skip=skip, limit=limit)
