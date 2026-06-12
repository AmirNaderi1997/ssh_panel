import asyncio
from backend.app.tasks.celery_app import celery_app
from backend.app.core.database import SessionLocal
from backend.app.core.logging import logger
from backend.app.services.server_service import ServerService
from backend.app.api.websocket import manager


def run_async(coro):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        return asyncio.ensure_future(coro)
    else:
        return asyncio.run(coro)


@celery_app.task(name="monitor_tasks.ping_servers")
def ping_servers_task():
    logger.info("Starting scheduled server ping and health checks task")
    
    async def _execute():
        async with SessionLocal() as db:
            server_service = ServerService(db)
            servers = await server_service.server_repo.get_multi()
            
            online_sessions = []
            server_loads = []
            
            for server in servers:
                try:
                    # Test SSH connectivity
                    is_online = await server_service.test_connection(server.id)
                    if is_online:
                        # Fetch server stats
                        stats = await server_service.health_check_server(server.id)
                        server_loads.append({
                            "server_name": server.name,
                            "cpu_percent": stats["cpu_percent"],
                            "ram_percent": stats["ram_percent"]
                        })
                        
                        # Fetch active SSH sessions
                        sessions = await server_service.ssh_service.get_active_sessions(server)
                        # Map sessions to include server details
                        for session in sessions:
                            online_sessions.append({
                                "username": session["username"],
                                "source_ip": session["source_ip"],
                                "login_time": session["login_time"],
                                "connected_server": server.name
                            })
                except Exception as e:
                    logger.error("Error performing health check on server", server=server.name, error=str(e))
            
            # Commit connection changes
            await db.commit()
            
            # Broadcast updates to WebSockets
            # 1. Broadcast online users list
            await manager.broadcast(
                {"event": "online_users_update", "data": online_sessions},
                "online_users"
            )
            
            # 2. Broadcast dashboard resources updates
            await manager.broadcast(
                {"event": "server_loads_update", "data": server_loads},
                "dashboard"
            )

    return run_async(_execute())
