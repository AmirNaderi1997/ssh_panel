import uuid
from typing import List
from fastapi import APIRouter, Depends, status, Query
from backend.app.core.permissions import Permission, PermissionChecker
from backend.app.dependencies import DBDep, ActiveAdminDep
from backend.app.schemas.user import SSHUserCreate, SSHUserResponse, SSHUserUpdate, SSHUserBulkCreate
from backend.app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["SSH User Management"])


@router.get(
    "",
    response_model=List[SSHUserResponse],
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_USERS))],
)
async def list_users(
    db: DBDep,
    server_id: uuid.UUID | None = None,
    reseller_id: uuid.UUID | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> List[SSHUserResponse]:
    """Retrieve all SSH VPN accounts with optional filters."""
    user_service = UserService(db)
    
    # We can fetch directly using custom filters in repository if passed
    # If reseller_id or server_id are specified, filter accordingly
    if server_id:
        return await user_service.user_repo.get_by_server(server_id, skip=skip, limit=limit)
    if reseller_id:
        return await user_service.user_repo.get_by_reseller(reseller_id, skip=skip, limit=limit)
    if status:
        return await user_service.user_repo.get_users_by_status(status, skip=skip, limit=limit)
        
    return await user_service.user_repo.get_multi(skip=skip, limit=limit)


@router.post(
    "",
    response_model=SSHUserResponse,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_USERS))],
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    db: DBDep, user_in: SSHUserCreate, current_admin: ActiveAdminDep
) -> SSHUserResponse:
    """Create a new SSH VPN user account on a remote server."""
    user_service = UserService(db)
    return await user_service.create_user(user_in, current_admin)


@router.post(
    "/bulk",
    response_model=List[SSHUserResponse],
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_USERS))],
    status_code=status.HTTP_201_CREATED,
)
async def bulk_create_users(
    db: DBDep, bulk_in: SSHUserBulkCreate, current_admin: ActiveAdminDep
) -> List[SSHUserResponse]:
    """Create multiple SSH user accounts in bulk."""
    user_service = UserService(db)
    return await user_service.bulk_create_users(bulk_in, current_admin)


@router.get(
    "/{user_id}",
    response_model=SSHUserResponse,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_USERS))],
)
async def get_user(db: DBDep, user_id: uuid.UUID) -> SSHUserResponse:
    """Retrieve details of a single SSH user account."""
    user_service = UserService(db)
    user = await user_service.user_repo.get(user_id)
    if not user:
        from backend.app.core.exceptions import EntityNotFoundException
        raise EntityNotFoundException("SSHUser", user_id)
    return user


@router.put(
    "/{user_id}",
    response_model=SSHUserResponse,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_USERS))],
)
async def update_user(
    db: DBDep, user_id: uuid.UUID, user_in: SSHUserUpdate
) -> SSHUserResponse:
    """Update SSH user configuration, password, or expiration."""
    user_service = UserService(db)
    return await user_service.update_user(user_id, user_in)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_USERS))],
)
async def delete_user(db: DBDep, user_id: uuid.UUID):
    """Delete an SSH user account from the DB and the remote server."""
    user_service = UserService(db)
    await user_service.delete_user(user_id)


@router.post(
    "/{user_id}/suspend",
    response_model=SSHUserResponse,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_USERS))],
)
async def suspend_user(db: DBDep, user_id: uuid.UUID) -> SSHUserResponse:
    """Lock user's Linux system account to prevent tunneling access."""
    user_service = UserService(db)
    return await user_service.suspend_user(user_id)


@router.post(
    "/{user_id}/activate",
    response_model=SSHUserResponse,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_USERS))],
)
async def activate_user(db: DBDep, user_id: uuid.UUID) -> SSHUserResponse:
    """Unlock user's Linux system account, restoring access."""
    user_service = UserService(db)
    return await user_service.activate_user(user_id)
