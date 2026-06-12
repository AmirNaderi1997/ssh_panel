import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from backend.app.core.permissions import Permission, PermissionChecker
from backend.app.dependencies import DBDep
from backend.app.schemas.domain import DomainCreate, DomainResponse
from backend.app.services.ssl_service import SSLService

router = APIRouter(prefix="/domains", tags=["Domain Management"])


@router.get(
    "",
    response_model=List[DomainResponse],
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_DOMAINS))],
)
async def list_domains(db: DBDep, skip: int = 0, limit: int = 100) -> List[DomainResponse]:
    """Retrieve list of all registered domains linked to the panel or routing nodes."""
    ssl_service = SSLService(db)
    return await ssl_service.domain_repo.get_multi(skip=skip, limit=limit)


@router.post(
    "",
    response_model=DomainResponse,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_DOMAINS))],
    status_code=status.HTTP_201_CREATED,
)
async def register_domain(db: DBDep, domain_in: DomainCreate) -> DomainResponse:
    """Register a new domain name mapping to a VPN node."""
    ssl_service = SSLService(db)
    if not domain_in.server_id:
        from backend.app.core.exceptions import BusinessRuleException
        raise BusinessRuleException("Target server ID is required to link domain")
    return await ssl_service.add_domain(domain_in.domain, domain_in.type, domain_in.server_id)


@router.delete(
    "/{domain_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_DOMAINS))],
)
async def remove_domain(db: DBDep, domain_id: uuid.UUID):
    """Deregister and delete a domain name."""
    ssl_service = SSLService(db)
    domain = await ssl_service.domain_repo.get(domain_id)
    if not domain:
        from backend.app.core.exceptions import EntityNotFoundException
        raise EntityNotFoundException("Domain", domain_id)
    await ssl_service.domain_repo.remove(domain_id)


@router.post(
    "/{domain_id}/verify-dns",
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_DOMAINS))],
)
async def verify_domain_dns_propagation(db: DBDep, domain_id: uuid.UUID):
    """Trigger an immediate DNS query to check domain A record routing configuration."""
    ssl_service = SSLService(db)
    is_verified = await ssl_service.verify_dns(domain_id)
    return {"verified": is_verified, "status": "VERIFIED" if is_verified else "FAILED"}
