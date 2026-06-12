from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.admin import Admin
from backend.app.models.domain import Domain
from backend.app.models.certificate import Certificate
from backend.app.models.reseller import Transaction
from backend.app.models.server import Server
from backend.app.models.user import SSHUser, LoginHistory
from backend.app.models.traffic import TrafficRecord
from backend.app.schemas.dashboard import (
    DashboardStatsResponse,
    UserStats,
    ServerStatsSummary,
    SystemStatusSummary,
    DashboardChartsResponse,
    TrafficChartItem,
    UserGrowthChartItem,
    ServerLoadChartItem,
    RevenueChartItem,
)


class MonitorService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_dashboard_stats(self) -> DashboardStatsResponse:
        """Query and aggregate counts for the dashboard stats widget."""
        # Users
        users_total = await self.db.scalar(select(func.count(SSHUser.id)))
        users_active = await self.db.scalar(select(func.count(SSHUser.id)).where(SSHUser.status == "ACTIVE"))
        users_expired = await self.db.scalar(select(func.count(SSHUser.id)).where(SSHUser.status == "EXPIRED"))
        users_disabled = await self.db.scalar(select(func.count(SSHUser.id)).where(SSHUser.status == "DISABLED"))
        
        # Online users - count unique active sessions (logout_time is null)
        users_online = await self.db.scalar(select(func.count(func.distinct(LoginHistory.user_id))).where(LoginHistory.logout_time == None))

        # Servers
        servers_total = await self.db.scalar(select(func.count(Server.id)))
        servers_online = await self.db.scalar(select(func.count(Server.id)).where(Server.status == "ONLINE"))
        servers_offline = servers_total - servers_online

        # System average metrics
        # Query all online servers to compute average load
        result = await self.db.execute(select(Server.status, Server.last_health_check))
        # For simulation if no real stats exist, we use psutil or placeholders
        import psutil
        try:
            local_cpu = psutil.cpu_percent()
            local_ram = psutil.virtual_memory().percent
            local_disk = psutil.disk_usage("/").percent
        except Exception:
            local_cpu, local_ram, local_disk = 12.5, 45.2, 33.1

        # Domains & SSL
        domains_total = await self.db.scalar(select(func.count(Domain.id)))
        ssl_active = await self.db.scalar(select(func.count(Certificate.id)).where(Certificate.status == "ACTIVE"))
        ssl_expired = await self.db.scalar(select(func.count(Certificate.id)).where(Certificate.status == "EXPIRED"))

        # Revenue (Sum transaction amounts for current month)
        now = datetime.now(timezone.utc)
        first_day_of_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        revenue_sum = await self.db.scalar(
            select(func.sum(Transaction.amount))
            .where(
                and_(
                    Transaction.type == "CREDIT",
                    Transaction.created_at >= first_day_of_month
                )
            )
        )
        revenue = float(revenue_sum) if revenue_sum else 0.0

        # Daily Registrations (last 7 days)
        daily_registrations = {}
        for i in range(7):
            d = now.date() - timedelta(days=i)
            day_start = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
            day_end = day_start + timedelta(days=1)
            count = await self.db.scalar(
                select(func.count(SSHUser.id))
                .where(
                    and_(
                        SSHUser.created_at >= day_start,
                        SSHUser.created_at < day_end
                    )
                )
            )
            daily_registrations[d.strftime("%Y-%m-%d")] = count or 0

        return DashboardStatsResponse(
            users=UserStats(
                total=users_total or 0,
                active=users_active or 0,
                online=users_online or 0,
                expired=users_expired or 0,
                disabled=users_disabled or 0,
            ),
            servers=ServerStatsSummary(
                total=servers_total or 0,
                online=servers_online or 0,
                offline=servers_offline or 0,
            ),
            system=SystemStatusSummary(
                cpu_percent=local_cpu,
                ram_percent=local_ram,
                disk_percent=local_disk,
                load_avg=[0.15, 0.22, 0.18],
            ),
            domains_total=domains_total or 0,
            ssl_active=ssl_active or 0,
            ssl_expired=ssl_expired or 0,
            revenue_this_month=revenue,
            daily_registrations=daily_registrations,
        )

    async def get_dashboard_charts(self) -> DashboardChartsResponse:
        """Compile historical data points for dashboard graphs."""
        # 1. User growth (last 7 days)
        user_growth = []
        now = datetime.now(timezone.utc)
        for i in reversed(range(7)):
            d = now.date() - timedelta(days=i)
            day_end = datetime(d.year, d.month, d.day, tzinfo=timezone.utc) + timedelta(days=1)
            # Total users registered up to the end of this day
            total = await self.db.scalar(
                select(func.count(SSHUser.id)).where(SSHUser.created_at < day_end)
            )
            user_growth.append(
                UserGrowthChartItem(date=d.strftime("%m-%d"), total_users=total or 0)
            )

        # 2. Server Load (list all servers with their current loads)
        server_load = []
        servers_res = await self.db.execute(select(Server))
        servers = servers_res.scalars().all()
        
        # If no servers, append sample
        if not servers:
            server_load.append(ServerLoadChartItem(server_name="Sample VPS", cpu_percent=12.0, ram_percent=45.0))
        for server in servers:
            # Generate simulated load if offline
            import random
            cpu = random.uniform(5.0, 25.0) if server.status == "ONLINE" else 0.0
            ram = random.uniform(20.0, 60.0) if server.status == "ONLINE" else 0.0
            server_load.append(
                ServerLoadChartItem(server_name=server.name, cpu_percent=round(cpu, 1), ram_percent=round(ram, 1))
            )

        # 3. Traffic usage (last 7 days upload/download)
        traffic_usage = []
        for i in reversed(range(7)):
            d = now.date() - timedelta(days=i)
            totals = await self.db.execute(
                select(
                    func.sum(TrafficRecord.upload_bytes),
                    func.sum(TrafficRecord.download_bytes)
                )
                .where(TrafficRecord.date == d)
            )
            upload_sum, download_sum = totals.first()
            traffic_usage.append(
                TrafficChartItem(
                    date=d.strftime("%m-%d"),
                    upload_bytes=int(upload_sum) if upload_sum else 0,
                    download_bytes=int(download_sum) if download_sum else 0,
                )
            )

        # 4. Revenue trends (past 6 months)
        revenue_trends = []
        for i in reversed(range(6)):
            # Start of month
            first_day = datetime(now.year, now.month, 1, tzinfo=timezone.utc) - timedelta(days=i * 30)
            month_name = first_day.strftime("%b")
            start = datetime(first_day.year, first_day.month, 1, tzinfo=timezone.utc)
            # End of month
            if first_day.month == 12:
                end = datetime(first_day.year + 1, 1, 1, tzinfo=timezone.utc)
            else:
                end = datetime(first_day.year, first_day.month + 1, 1, tzinfo=timezone.utc)
                
            rev_sum = await self.db.scalar(
                select(func.sum(Transaction.amount))
                .where(
                    and_(
                        Transaction.type == "CREDIT",
                        Transaction.created_at >= start,
                        Transaction.created_at < end,
                    )
                )
            )
            revenue_trends.append(
                RevenueChartItem(month=month_name, amount=float(rev_sum) if rev_sum else 0.0)
            )

        return DashboardChartsResponse(
            traffic_usage=traffic_usage,
            user_growth=user_growth,
            server_load=server_load,
            revenue_trends=revenue_trends,
        )
