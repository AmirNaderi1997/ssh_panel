from fastapi import APIRouter
from backend.app.api.v1 import auth, admin, servers, users, dashboard, traffic, domains, ssl, resellers, backups

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(servers.router)
api_router.include_router(users.router)
api_router.include_router(dashboard.router)
api_router.include_router(traffic.router)
api_router.include_router(domains.router)
api_router.include_router(ssl.router)
api_router.include_router(resellers.router)
api_router.include_router(backups.router)




