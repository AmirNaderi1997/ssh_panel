import uuid
from typing import List
from decimal import Decimal
from fastapi import APIRouter, Depends, status, Query
from backend.app.core.permissions import Permission, PermissionChecker
from backend.app.dependencies import DBDep, ActiveAdminDep
from backend.app.schemas.reseller import (
    ResellerCreate,
    ResellerResponse,
    TransactionResponse,
)
from backend.app.services.reseller_service import ResellerService

router = APIRouter(prefix="/resellers", tags=["Resellers & Credit Billing"])


@router.get(
    "",
    response_model=List[ResellerResponse],
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_RESELLERS))],
)
async def list_resellers(db: DBDep, skip: int = 0, limit: int = 100) -> List[ResellerResponse]:
    """Retrieve list of all registered reseller profiles."""
    reseller_service = ResellerService(db)
    return await reseller_service.reseller_repo.get_multi(skip=skip, limit=limit)


@router.post(
    "",
    response_model=ResellerResponse,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_RESELLERS))],
    status_code=status.HTTP_201_CREATED,
)
async def register_reseller(db: DBDep, reseller_in: ResellerCreate) -> ResellerResponse:
    """Initialize a reseller profile for an existing administrator account."""
    reseller_service = ResellerService(db)
    return await reseller_service.create_reseller(
        reseller_in.admin_id, max_users=reseller_in.max_users
    )


@router.post(
    "/{reseller_id}/allocate",
    response_model=TransactionResponse,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_RESELLERS))],
)
async def allocate_credits_to_reseller(
    db: DBDep,
    reseller_id: uuid.UUID,
    amount: Decimal = Query(..., description="Amount of credits to allocate"),
    description: str = Query("Credit top up", description="Allocation remarks"),
    current_admin: ActiveAdminDep = None
) -> TransactionResponse:
    """Top up credit balance for a reseller."""
    reseller_service = ResellerService(db)
    return await reseller_service.allocate_credits(
        reseller_id, amount, description, current_admin.id
    )


@router.post(
    "/{reseller_id}/deduct",
    response_model=TransactionResponse,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_RESELLERS))],
)
async def deduct_credits_from_reseller(
    db: DBDep,
    reseller_id: uuid.UUID,
    amount: Decimal = Query(..., description="Amount of credits to deduct"),
    description: str = Query("Credit reduction", description="Deduction remarks"),
    current_admin: ActiveAdminDep = None
) -> TransactionResponse:
    """Deduct credit balance from a reseller."""
    reseller_service = ResellerService(db)
    return await reseller_service.deduct_credits(
        reseller_id, amount, description, current_admin.id
    )


@router.get(
    "/{reseller_id}/transactions",
    response_model=List[TransactionResponse],
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_RESELLERS))],
)
async def list_reseller_transactions(
    db: DBDep,
    reseller_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100
) -> List[TransactionResponse]:
    """Retrieve credit logs and transactional history for a reseller."""
    reseller_service = ResellerService(db)
    return await reseller_service.transaction_repo.get_by_reseller(
        reseller_id, skip=skip, limit=limit
    )
