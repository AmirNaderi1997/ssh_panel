import uuid
from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.config import settings
from backend.app.core.database import get_db
from backend.app.core.exceptions import InvalidCredentialsException
from backend.app.core.security import verify_token
from backend.app.models.admin import Admin
from backend.app.repositories.admin_repo import AdminRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

DBDep = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_current_admin(db: DBDep, token: TokenDep) -> Admin:
    """Retrieve the currently authenticated admin from the token payload."""
    payload = verify_token(token)
    if not payload or payload.get("type") != "access":
        raise InvalidCredentialsException("Could not validate credentials")
        
    admin_id_str = payload.get("sub")
    if not admin_id_str:
        raise InvalidCredentialsException("Invalid token subject")
        
    try:
        admin_id = uuid.UUID(admin_id_str)
    except ValueError:
        raise InvalidCredentialsException("Invalid token subject format")

    admin_repo = AdminRepository(db)
    admin = await admin_repo.get(admin_id)
    if not admin:
        raise InvalidCredentialsException("User not found")
        
    return admin


async def get_current_active_admin(
    current_admin: Annotated[Admin, Depends(get_current_admin)]
) -> Admin:
    """Dependency that ensures the authenticated admin is active."""
    if not current_admin.is_active:
        raise InvalidCredentialsException("Inactive user account")
    return current_admin


# Define dependency injection alias
ActiveAdminDep = Annotated[Admin, Depends(get_current_active_admin)]
