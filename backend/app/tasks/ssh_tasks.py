import asyncio
import uuid
from backend.app.tasks.celery_app import celery_app
from backend.app.core.database import SessionLocal
from backend.app.core.logging import logger
from backend.app.repositories.user_repo import UserRepository
from backend.app.repositories.admin_repo import AdminRepository
from backend.app.schemas.user import SSHUserCreate
from backend.app.services.user_service import UserService


def run_async(coro):
    """Helper to run async coroutines inside synchronous Celery tasks."""
    loop = asyncio.get_event_loop()
    if loop.is_running():
        return asyncio.ensure_future(coro)
    else:
        return asyncio.run(coro)


@celery_app.task(name="ssh_tasks.create_user")
def create_user_task(server_id: str, user_id: str, creator_id: str):
    logger.info("Executing async SSH user creation task", server_id=server_id, user_id=user_id)
    
    async def _execute():
        async with SessionLocal() as db:
            user_repo = UserRepository(db)
            admin_repo = AdminRepository(db)
            
            user = await user_repo.get(uuid.UUID(user_id))
            admin = await admin_repo.get(uuid.UUID(creator_id))
            
            if not user or not admin:
                logger.error("User or Creator Admin not found for SSH task", user_id=user_id, creator_id=creator_id)
                return False
                
            user_service = UserService(db)
            
            # Since the user is already created in DB in the API request, we just need to execute
            # the SSH creation commands. Let's make a method or call create_linux_user directly.
            # We fetch user decrypted password
            from backend.app.core.security import decrypt_field
            clear_password = decrypt_field(user.password_encrypted)
            
            try:
                await user_service.ssh_service.create_linux_user(
                    server=user.server,
                    username=user.username,
                    password=clear_password,
                    expiry=user.expiration_date
                )
                logger.info("Successfully executed SSH user creation", username=user.username)
                return True
            except Exception as e:
                logger.error("Failed to execute SSH user creation", username=user.username, error=str(e))
                # Update status to error/disabled if SSH creation failed
                user.status = "DISABLED"
                user.notes = f"SSH creation failed: {str(e)}"
                db.add(user)
                await db.commit()
                return False

    return run_async(_execute())


@celery_app.task(name="ssh_tasks.delete_user")
def delete_user_task(server_id: str, username: str):
    logger.info("Executing async SSH user deletion task", server_id=server_id, username=username)
    
    async def _execute():
        async with SessionLocal() as db:
            from backend.app.repositories.server_repo import ServerRepository
            server_repo = ServerRepository(db)
            server = await server_repo.get(uuid.UUID(server_id))
            if not server:
                logger.error("Server not found for SSH delete task", server_id=server_id)
                return False
                
            user_service = UserService(db)
            try:
                await user_service.ssh_service.delete_linux_user(server, username)
                logger.info("Successfully executed SSH user deletion", username=username)
                return True
            except Exception as e:
                logger.error("Failed to execute SSH user deletion", username=username, error=str(e))
                return False

    return run_async(_execute())
