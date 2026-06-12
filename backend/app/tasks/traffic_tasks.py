import asyncio
from backend.app.tasks.celery_app import celery_app
from backend.app.core.database import SessionLocal
from backend.app.core.logging import logger
from backend.app.services.traffic_service import TrafficService


def run_async(coro):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        return asyncio.ensure_future(coro)
    else:
        return asyncio.run(coro)


@celery_app.task(name="traffic_tasks.collect_traffic")
def collect_traffic_task():
    logger.info("Starting scheduled traffic collection task")
    
    async def _execute():
        async with SessionLocal() as db:
            from backend.app.repositories.server_repo import ServerRepository
            server_repo = ServerRepository(db)
            servers = await server_repo.get_multi()
            
            traffic_service = TrafficService(db)
            
            # Collect traffic for each server
            for server in servers:
                try:
                    await traffic_service.collect_server_traffic(server.id)
                except Exception as e:
                    logger.error("Error collecting traffic for server", server=server.name, error=str(e))
            
            # Enforce traffic quotas and suspend users if needed
            try:
                await traffic_service.enforce_traffic_quotas()
            except Exception as e:
                logger.error("Error enforcing traffic quotas", error=str(e))
                
            await db.commit()

    return run_async(_execute())
