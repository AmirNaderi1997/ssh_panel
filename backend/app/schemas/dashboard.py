from typing import Dict, List, Any
from pydantic import BaseModel


class SystemStatusSummary(BaseModel):
    cpu_percent: float = 0.0
    ram_percent: float = 0.0
    disk_percent: float = 0.0
    load_avg: List[float] = [0.0, 0.0, 0.0]


class UserStats(BaseModel):
    total: int = 0
    active: int = 0
    online: int = 0
    expired: int = 0
    disabled: int = 0


class ServerStatsSummary(BaseModel):
    total: int = 0
    online: int = 0
    offline: int = 0


class DashboardStatsResponse(BaseModel):
    users: UserStats
    servers: ServerStatsSummary
    system: SystemStatusSummary
    domains_total: int = 0
    ssl_active: int = 0
    ssl_expired: int = 0
    revenue_this_month: float = 0.0
    daily_registrations: Dict[str, int] = {}


class TrafficChartItem(BaseModel):
    date: str
    upload_bytes: int
    download_bytes: int


class UserGrowthChartItem(BaseModel):
    date: str
    total_users: int


class ServerLoadChartItem(BaseModel):
    server_name: str
    cpu_percent: float
    ram_percent: float


class RevenueChartItem(BaseModel):
    month: str
    amount: float


class DashboardChartsResponse(BaseModel):
    traffic_usage: List[TrafficChartItem] = []
    user_growth: List[UserGrowthChartItem] = []
    server_load: List[ServerLoadChartItem] = []
    revenue_trends: List[RevenueChartItem] = []
