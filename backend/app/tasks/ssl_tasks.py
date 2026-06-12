import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from backend.app.tasks.celery_app import celery_app
from backend.app.core.database import SessionLocal
from backend.app.core.logging import logger
from backend.app.services.ssl_service import SSLService


def run_async(coro):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        return asyncio.ensure_future(coro)
    else:
        return asyncio.run(coro)


@celery_app.task(name="ssl_tasks.auto_renew_certificates")
def auto_renew_certificates_task():
    logger.info("Executing scheduled SSL auto renewal check task")
    
    async def _execute():
        async with SessionLocal() as db:
            ssl_service = SSLService(db)
            
            # Query certificates expiring within next 15 days
            from backend.app.models.certificate import Certificate
            from sqlalchemy import select, and_
            
            expiry_threshold = datetime.now(timezone.utc) + timedelta(days=15)
            query = select(Certificate).where(
                and_(
                    Certificate.status == "ACTIVE",
                    Certificate.expiration_date <= expiry_threshold,
                    Certificate.auto_renew == True
                )
            )
            result = await db.execute(query)
            expiring_certs = result.scalars().all()
            
            for cert in expiring_certs:
                logger.info("Auto-renewing certificate", domain_id=cert.domain_id, expiration=cert.expiration_date)
                try:
                    await ssl_service.issue_and_deploy_ssl(cert.domain_id)
                    logger.info("Auto-renewal successful for domain cert", domain_id=cert.domain_id)
                except Exception as e:
                    logger.error("Failed to auto-renew certificate", domain_id=cert.domain_id, error=str(e))
            
            await db.commit()

    return run_async(_execute())
