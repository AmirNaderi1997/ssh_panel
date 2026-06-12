import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from backend.app.core.permissions import Permission, PermissionChecker
from backend.app.dependencies import DBDep
from backend.app.schemas.server import (
    ServerCreate,
    ServerResponse,
    ServerUpdate,
    ServerGroupCreate,
    ServerGroupResponse,
)
from backend.app.services.server_service import ServerService

router = APIRouter(prefix="/servers", tags=["Server Management"])


@router.get(
    "",
    response_model=List[ServerResponse],
    dependencies=[Depends(PermissionChecker(Permission.VIEW_TRAFFIC))],  # Support or above can view
)
async def list_servers(db: DBDep, skip: int = 0, limit: int = 100) -> List[ServerResponse]:
    """Retrieve list of all registered remote servers."""
    server_service = ServerService(db)
    return await server_service.server_repo.get_multi(skip=skip, limit=limit)


@router.post(
    "",
    response_model=ServerResponse,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_SERVERS))],
    status_code=status.HTTP_201_CREATED,
)
async def add_server(db: DBDep, server_in: ServerCreate) -> ServerResponse:
    """Register a new remote VPS instance."""
    server_service = ServerService(db)
    return await server_service.add_server(server_in)


@router.get(
    "/{server_id}",
    response_model=ServerResponse,
    dependencies=[Depends(PermissionChecker(Permission.VIEW_TRAFFIC))],
)
async def get_server(db: DBDep, server_id: uuid.UUID) -> ServerResponse:
    """Retrieve a single server profile by its UUID."""
    server_service = ServerService(db)
    server = await server_service.server_repo.get(server_id)
    if not server:
        from backend.app.core.exceptions import EntityNotFoundException
        raise EntityNotFoundException("Server", server_id)
    return server


@router.put(
    "/{server_id}",
    response_model=ServerResponse,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_SERVERS))],
)
async def update_server(
    db: DBDep, server_id: uuid.UUID, server_in: ServerUpdate
) -> ServerResponse:
    """Update remote server credentials or configurations."""
    server_service = ServerService(db)
    return await server_service.update_server(server_id, server_in)


@router.delete(
    "/{server_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_SERVERS))],
)
async def remove_server(db: DBDep, server_id: uuid.UUID):
    """Deregister and remove a server."""
    server_service = ServerService(db)
    server = await server_service.server_repo.get(server_id)
    if not server:
        from backend.app.core.exceptions import EntityNotFoundException
        raise EntityNotFoundException("Server", server_id)
    await server_service.server_repo.remove(server_id)


@router.post(
    "/{server_id}/test",
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_SERVERS))],
)
async def test_server_connectivity(db: DBDep, server_id: uuid.UUID):
    """Test connection to the server via SSH."""
    server_service = ServerService(db)
    is_online = await server_service.test_connection(server_id)
    return {"status": "ONLINE" if is_online else "OFFLINE", "connected": is_online}


@router.post(
    "/{server_id}/stats",
    dependencies=[Depends(PermissionChecker(Permission.VIEW_TRAFFIC))],
)
async def check_server_health_metrics(db: DBDep, server_id: uuid.UUID):
    """Query and fetch system health utilization stats from the remote host."""
    server_service = ServerService(db)
    stats = await server_service.health_check_server(server_id)
    return stats


# Groups
@router.post(
    "/groups",
    response_model=ServerGroupResponse,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_SERVERS))],
)
async def create_server_group(db: DBDep, group_in: ServerGroupCreate) -> ServerGroupResponse:
    server_service = ServerService(db)
    return await server_service.create_group(group_in)


@router.delete(
    "/groups/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_SERVERS))],
)
async def delete_server_group(db: DBDep, group_id: uuid.UUID):
    server_service = ServerService(db)
    await server_service.delete_group(group_id)
