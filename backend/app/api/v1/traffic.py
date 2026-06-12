import uuid
from typing import List
from datetime import date, timedelta
from fastapi import APIRouter, Depends, status, Query
from backend.app.core.permissions import Permission, PermissionChecker
from backend.app.dependencies import DBDep
from backend.app.schemas.traffic import TrafficRecordResponse
from backend.app.services.traffic_service import TrafficService

router = APIRouter(prefix="/traffic", tags=["Traffic & Accounting"])


@router.get(
    "/users/{user_id}",
    response_model=List[TrafficRecordResponse],
    dependencies=[Depends(PermissionChecker(Permission.VIEW_TRAFFIC))],
)
async def get_user_traffic_history(
    db: DBDep,
    user_id: uuid.UUID,
    days: int = Query(7, description="Number of historical days to fetch"),
) -> List[TrafficRecordResponse]:
    """Retrieve daily traffic consumption history for a specific SSH user account."""
    traffic_service = TrafficService(db)
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    return await traffic_service.record_repo.get_by_user_range(user_id, start_date, end_date)


@router.post(
    "/reset/{user_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(PermissionChecker(Permission.MANAGE_USERS))],
)
async def reset_user_traffic_counters(db: DBDep, user_id: uuid.UUID):
    """Reset the accumulated traffic counter for an SSH account to zero."""
    traffic_service = TrafficService(db)
    await traffic_service.reset_user_traffic(user_id)
    return {"message": "Traffic counters successfully reset to zero"}
