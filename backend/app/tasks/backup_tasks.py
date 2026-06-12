import asyncio
import uuid
from backend.app.tasks.celery_app import celery_app
from backend.app.core.database import SessionLocal
from backend.app.core.logging import logger
from backend.app.services.backup_service import BackupService


def run_async(coro):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        return asyncio.ensure_future(coro)
    else:
        return asyncio.run(coro)


@celery_app.task(name="backup_tasks.scheduled_backup")
def scheduled_backup_task(notes: str = "Scheduled automated backup"):
    logger.info("Executing scheduled automated database backup task")
    
    async def _execute():
        async with SessionLocal() as db:
            backup_service = BackupService(db)
            try:
                backup = await backup_service.create_db_backup(
                    notes=notes,
                    creator_id=None # None indicates automated scheduled run
                )
                logger.info("Scheduled backup successfully generated", file=backup.filename)
                await db.commit()
                return True
            except Exception as e:
                logger.error("Scheduled backup generation failed", error=str(e))
                return False

    return run_async(_execute())
