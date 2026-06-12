import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.exceptions import InvalidCredentialsException, BusinessRuleException
from backend.app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    generate_totp_secret,
    get_totp_uri,
    verify_totp_code,
)
from backend.app.models.admin import Admin
from backend.app.repositories.admin_repo import AdminRepository
from backend.app.schemas.auth import AdminCreate, LoginRequest, Token, Setup2FAResponse


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.admin_repo = AdminRepository(db)

    async def authenticate_admin(self, login_data: LoginRequest) -> Admin:
        """Authenticate an admin user, checking password and TOTP if enabled."""
        admin = await self.admin_repo.get_by_username(login_data.username)
        if not admin or not admin.is_active:
            raise InvalidCredentialsException()

        if not verify_password(login_data.password, admin.password_hash):
            raise InvalidCredentialsException()

        if admin.totp_enabled:
            if not login_data.totp_code:
                raise InvalidCredentialsException("2FA code required")
            if not verify_totp_code(admin.totp_secret, login_data.totp_code):
                raise InvalidCredentialsException("Invalid 2FA code")

        # Update last login
        admin.last_login = datetime.now(timezone.utc)
        self.db.add(admin)
        await self.db.flush()
        
        return admin

    async def register_admin(self, admin_in: AdminCreate) -> Admin:
        """Register a new admin user."""
        existing_username = await self.admin_repo.get_by_username(admin_in.username)
        if existing_username:
            raise BusinessRuleException("Username already registered")

        existing_email = await self.admin_repo.get_by_email(admin_in.email)
        if existing_email:
            raise BusinessRuleException("Email already registered")

        # Hash password and create admin
        db_obj = Admin(
            username=admin_in.username,
            email=admin_in.email,
            password_hash=hash_password(admin_in.password),
            role=admin_in.role,
            permissions=admin_in.permissions,
        )
        self.db.add(db_obj)
        await self.db.flush()
        return db_obj

    async def create_tokens_for_admin(self, admin: Admin) -> Token:
        """Generate JWT access and refresh tokens for an authenticated admin."""
        access_token = create_access_token(subject=admin.id)
        refresh_token = create_refresh_token(subject=admin.id)
        return Token(access_token=access_token, refresh_token=refresh_token)

    async def refresh_access_token(self, refresh_token: str) -> str:
        """Generate a new access token from a valid refresh token."""
        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise InvalidCredentialsException("Invalid refresh token")
        
        admin_id = payload.get("sub")
        if not admin_id:
            raise InvalidCredentialsException("Invalid token payload")

        try:
            admin_uuid = uuid.UUID(admin_id)
        except ValueError:
            raise InvalidCredentialsException("Invalid token subject format")
            
        admin = await self.admin_repo.get(admin_uuid)
        if not admin or not admin.is_active:
            raise InvalidCredentialsException("User not found or inactive")

        return create_access_token(subject=admin_id)

    async def setup_totp(self, admin: Admin) -> Setup2FAResponse:
        """Initialize TOTP configuration for an admin (does not enable 2FA yet)."""
        secret = generate_totp_secret()
        qr_uri = get_totp_uri(secret, admin.username)
        
        admin.totp_secret = secret
        self.db.add(admin)
        await self.db.flush()
        
        return Setup2FAResponse(secret=secret, qr_code_uri=qr_uri)

    async def verify_and_enable_totp(self, admin: Admin, code: str) -> bool:
        """Verify the first TOTP code to officially enable 2FA on the account."""
        if not admin.totp_secret:
            raise BusinessRuleException("2FA not initialized. Run setup first.")
            
        if verify_totp_code(admin.totp_secret, code):
            admin.totp_enabled = True
            self.db.add(admin)
            await self.db.flush()
            return True
            
        return False
        
    async def disable_totp(self, admin: Admin) -> None:
        """Disable TOTP 2FA on the admin account."""
        admin.totp_enabled = False
        admin.totp_secret = None
        self.db.add(admin)
        await self.db.flush()
