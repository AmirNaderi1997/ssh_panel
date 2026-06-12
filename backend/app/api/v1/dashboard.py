from fastapi import APIRouter, Depends
from backend.app.core.permissions import Permission, PermissionChecker
from backend.app.dependencies import DBDep
from backend.app.schemas.dashboard import DashboardStatsResponse, DashboardChartsResponse
from backend.app.services.monitor_service import MonitorService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/stats",
    response_model=DashboardStatsResponse,
    dependencies=[Depends(PermissionChecker(Permission.VIEW_TRAFFIC))],
)
async def get_dashboard_summary_stats(db: DBDep) -> DashboardStatsResponse:
    """Retrieve statistical aggregates for the dashboard widget view."""
    monitor_service = MonitorService(db)
    return await monitor_service.get_dashboard_stats()


@router.get(
    "/charts",
    response_model=DashboardChartsResponse,
    dependencies=[Depends(PermissionChecker(Permission.VIEW_TRAFFIC))],
)
async def get_dashboard_historical_charts(db: DBDep) -> DashboardChartsResponse:
    """Retrieve historical arrays for traffic, users, servers, and revenue charts."""
    monitor_service = MonitorService(db)
    return await monitor_service.get_dashboard_charts()
