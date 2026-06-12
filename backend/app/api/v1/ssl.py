import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from backend.app.core.permissions import Permission, PermissionChecker
from backend.app.dependencies import DBDep
from backend.app.schemas.certificate import CertificateResponse
from backend.app.services.ssl_service import SSLService

router = APIRouter(prefix="/ssl", tags=["SSL & ACME Automation"])


@router.post(
    "/issue/{domain_id}",
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_SSL))],
)
async def request_and_deploy_domain_certificate(db: DBDep, domain_id: uuid.UUID):
    """Trigger DNS checks, register ACME order, request SSL, and deploy key files to server Nginx."""
    ssl_service = SSLService(db)
    await ssl_service.issue_and_deploy_ssl(domain_id)
    return {"status": "SUCCESS", "message": "SSL Certificate issued and deployed successfully"}


@router.get(
    "/certificates",
    response_model=List[CertificateResponse],
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_SSL))],
)
async def list_registered_certificates(db: DBDep, skip: int = 0, limit: int = 100) -> List[CertificateResponse]:
    """Retrieve list of all active or pending SSL certificates."""
    ssl_service = SSLService(db)
    return await ssl_service.cert_repo.get_multi(skip=skip, limit=limit)
