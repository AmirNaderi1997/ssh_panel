from enum import Enum
from typing import List, Set
from fastapi import Depends
from backend.app.core.exceptions import PermissionDeniedException


class Role(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    SUPPORT = "SUPPORT"
    RESELLER = "RESELLER"


class Permission(str, Enum):
    MANAGE_USERS = "MANAGE_USERS"
    MANAGE_SERVERS = "MANAGE_SERVERS"
    MANAGE_DOMAINS = "MANAGE_DOMAINS"
    MANAGE_SSL = "MANAGE_SSL"
    MANAGE_RESELLERS = "MANAGE_RESELLERS"
    MANAGE_ADMINS = "MANAGE_ADMINS"
    VIEW_AUDIT = "VIEW_AUDIT"
    MANAGE_BACKUPS = "MANAGE_BACKUPS"
    VIEW_TRAFFIC = "VIEW_TRAFFIC"
    MANAGE_SETTINGS = "MANAGE_SETTINGS"


# Define default permissions for each role
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.SUPER_ADMIN: set(Permission),
    Role.ADMIN: {
        Permission.MANAGE_USERS,
        Permission.MANAGE_SERVERS,
        Permission.MANAGE_DOMAINS,
        Permission.MANAGE_SSL,
        Permission.MANAGE_RESELLERS,
        Permission.VIEW_AUDIT,
        Permission.MANAGE_BACKUPS,
        Permission.VIEW_TRAFFIC,
        Permission.MANAGE_SETTINGS,
    },
    Role.SUPPORT: {
        Permission.MANAGE_USERS,
        Permission.VIEW_TRAFFIC,
        Permission.VIEW_AUDIT,
    },
    Role.RESELLER: {
        Permission.MANAGE_USERS,  # Restricted to their own users in service layer
        Permission.VIEW_TRAFFIC,
    },
}


def has_permission(role: str, user_permissions_override: List[str] | None, required_permission: Permission) -> bool:
    """Check if the user with given role and permission overrides has the required permission."""
    try:
        user_role = Role(role)
    except ValueError:
        return False
    
    # 1. Check role's default permissions
    role_perms = ROLE_PERMISSIONS.get(user_role, set())
    if required_permission in role_perms:
        return True
        
    # 2. Check if user has explicit permission overrides
    if user_permissions_override and required_permission.value in user_permissions_override:
        return True
        
    return False


def PermissionChecker(permission: Permission):
    """Factory that returns a FastAPI dependency function to check permissions.
    
    Usage in routes:
        dependencies=[Depends(PermissionChecker(Permission.VIEW_TRAFFIC))]
    """
    from backend.app.dependencies import get_current_active_admin

    async def _check_permission(current_admin=Depends(get_current_active_admin)):
        if not current_admin:
            raise PermissionDeniedException("Not authenticated")
        
        overrides = current_admin.permissions if hasattr(current_admin, "permissions") else None
        
        if not has_permission(current_admin.role, overrides, permission):
            raise PermissionDeniedException(f"Missing required permission: {permission.value}")
        
        return current_admin

    return _check_permission
