from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.api.v1.router import api_router
from backend.app.config import settings
from backend.app.core.database import SessionLocal
from backend.app.core.exceptions import SSHManagerException
from backend.app.core.logging import setup_logging, logger
from backend.app.core.middleware import RequestLogMiddleware
from backend.app.models.admin import Admin
from backend.app.repositories.admin_repo import AdminRepository
from backend.app.schemas.auth import AdminCreate
from backend.app.services.auth_service import AuthService


async def seed_initial_admin() -> None:
    """Check if database is empty of admins, if so, seed superadmin."""
    async with SessionLocal() as db:
        try:
            admin_repo = AdminRepository(db)
            admins = await admin_repo.get_multi(limit=1)
            if not admins:
                logger.info("No admin accounts detected, seeding default superadmin")
                auth_service = AuthService(db)
                await auth_service.register_admin(
                    AdminCreate(
                        username="admin",
                        email="admin@example.com",
                        password="adminpassword123",
                        role="SUPER_ADMIN",
                        permissions=[],
                    )
                )
                await db.commit()
                logger.info("Default superadmin successfully seeded: admin / adminpassword123")
        except Exception as e:
            logger.error("Error during initial admin seeding", error=str(e))
            await db.rollback()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup structured logger
    setup_logging()
    logger.info("SSH Manager Pro starting up...")
    
    # Auto-create tables (useful for development/sqlite)
    from backend.app.models import Base
    from backend.app.core.database import engine
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database tables", error=str(e))
    
    # Run database initializations/seedings
    await seed_initial_admin()
    
    yield
    
    logger.info("SSH Manager Pro shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Custom HTTP Exception Handler for domain-specific errors
@app.exception_handler(SSHManagerException)
async def ssh_manager_exception_handler(request: Request, exc: SSHManagerException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


# Exception handler for general unhandled exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server error", error=str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred."},
    )


# Register middlewares
app.add_middleware(RequestLogMiddleware)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include main API router
app.include_router(api_router, prefix=settings.API_V1_STR)

from backend.app.api import websocket
app.include_router(websocket.router, prefix=settings.API_V1_STR)



@app.get("/health", tags=["Health"])
def health_check():
    """Simple API health check endpoint."""
    return {"status": "healthy", "service": settings.PROJECT_NAME}
