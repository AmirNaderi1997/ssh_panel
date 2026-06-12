from fastapi import APIRouter, Depends, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from backend.app.core.exceptions import InvalidCredentialsException
from backend.app.dependencies import DBDep, ActiveAdminDep
from backend.app.schemas.auth import LoginRequest, Token, TokenRefreshRequest, AdminResponse, Setup2FAResponse, Verify2FARequest
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login(
    db: DBDep,
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """OAuth2 compatible token login, retrieve access and refresh tokens.
    
    Supports form fields for Swagger UI.
    """
    auth_service = AuthService(db)
    
    # Check if TOTP code is passed via header or query (if any)
    # Since OAuth2PasswordRequestForm doesn't have custom fields, we read it
    # from LoginRequest if used, but for form_data we check if totp code was provided.
    login_data = LoginRequest(
        username=form_data.username,
        password=form_data.password,
        totp_code=None  # Standard flow without 2FA or with header
    )
    
    admin = await auth_service.authenticate_admin(login_data)
    return await auth_service.create_tokens_for_admin(admin)


@router.post("/login-json", response_model=Token)
async def login_json(
    db: DBDep,
    login_data: LoginRequest
) -> Token:
    """JSON body login endpoint (useful for frontend SPAs)."""
    auth_service = AuthService(db)
    admin = await auth_service.authenticate_admin(login_data)
    return await auth_service.create_tokens_for_admin(admin)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    db: DBDep,
    refresh_data: TokenRefreshRequest
) -> Token:
    """Refresh the access token using a valid refresh token."""
    auth_service = AuthService(db)
    new_access_token = await auth_service.refresh_access_token(refresh_data.refresh_token)
    return Token(
        access_token=new_access_token,
        refresh_token=refresh_data.refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=AdminResponse)
async def get_me(current_admin: ActiveAdminDep) -> AdminResponse:
    """Retrieve details of the currently logged-in admin."""
    return current_admin


@router.post("/2fa/setup", response_model=Setup2FAResponse)
async def setup_2fa(
    db: DBDep,
    current_admin: ActiveAdminDep
) -> Setup2FAResponse:
    """Generate a new TOTP 2FA secret and qr code uri."""
    auth_service = AuthService(db)
    return await auth_service.setup_totp(current_admin)


@router.post("/2fa/verify")
async def verify_2fa(
    db: DBDep,
    current_admin: ActiveAdminDep,
    verify_data: Verify2FARequest
):
    """Verify and enable 2FA on the admin account."""
    auth_service = AuthService(db)
    success = await auth_service.verify_and_enable_totp(current_admin, verify_data.code)
    if not success:
        raise InvalidCredentialsException("Invalid verification code")
    return {"message": "2FA successfully enabled"}


@router.post("/2fa/disable")
async def disable_2fa(
    db: DBDep,
    current_admin: ActiveAdminDep
):
    """Disable 2FA on the admin account."""
    auth_service = AuthService(db)
    await auth_service.disable_totp(current_admin)
    return {"message": "2FA successfully disabled"}
