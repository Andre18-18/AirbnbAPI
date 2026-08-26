from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.dependencies import get_current_admin, validate_csrf
from app.core.logging import security_logger
from app.core.rate_limit import rate_limit
from app.core.security import create_access_token, generate_token_urlsafe, hash_secret, normalize_email, verify_password, verify_secret
from app.db.session import get_db
from app.models.admin_user import AdminSession, AdminUser
from app.schemas.auth import AuthStatusResponse, AuthUserRead, LoginRequest

router = APIRouter(prefix="/admin/auth")

ACCESS_COOKIE = "admin_access_token"
REFRESH_COOKIE = "admin_refresh_token"
CSRF_COOKIE = "XSRF-TOKEN"
CSRF_HEADER = "x-csrf-token"


def set_auth_cookies(response: Response, access_token: str, refresh_token: str, csrf_token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        ACCESS_COOKIE,
        access_token,
        httponly=True,
        secure=settings.secure_cookies,
        samesite=settings.admin_cookie_samesite,
        max_age=settings.admin_access_token_expire_minutes * 60,
        path="/api",
    )
    response.set_cookie(
        REFRESH_COOKIE,
        refresh_token,
        httponly=True,
        secure=settings.secure_cookies,
        samesite=settings.admin_cookie_samesite,
        max_age=settings.admin_refresh_token_expire_days * 24 * 60 * 60,
        path="/api/admin/auth",
    )
    response.set_cookie(
        CSRF_COOKIE,
        csrf_token,
        httponly=False,
        secure=settings.secure_cookies,
        samesite=settings.admin_cookie_samesite,
        max_age=settings.admin_refresh_token_expire_days * 24 * 60 * 60,
        path="/",
    )


def clear_auth_cookies(response: Response) -> None:
    for name, path in [(ACCESS_COOKIE, "/api"), (REFRESH_COOKIE, "/api/admin/auth"), (CSRF_COOKIE, "/")]:
        response.delete_cookie(name, path=path)


async def create_session(db: AsyncSession, admin: AdminUser, request: Request) -> tuple[str, str, str]:
    settings = get_settings()
    refresh_token = generate_token_urlsafe()
    csrf_token = generate_token_urlsafe()
    session = AdminSession(
        user_id=admin.id,
        refresh_token_hash=hash_secret(refresh_token),
        csrf_token_hash=hash_secret(csrf_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.admin_refresh_token_expire_days),
        user_agent=request.headers.get("user-agent", "")[:300] or None,
        ip_address=request.client.host[:80] if request.client else None,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return create_access_token(admin.id, session.id), refresh_token, csrf_token


@router.post("/login", response_model=AuthStatusResponse)
async def login(payload: LoginRequest, request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    rate_limit(request, f"login:{normalize_email(str(payload.email))}", limit=5, window_seconds=300)
    email = normalize_email(str(payload.email))
    result = await db.execute(select(AdminUser).where(AdminUser.email == email))
    admin = result.scalar_one_or_none()
    if not admin or not admin.active or not verify_password(payload.password, admin.password_hash):
        security_logger.warning("admin_login_failed email=%s ip=%s", email, request.client.host if request.client else "unknown")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token, refresh_token, csrf_token = await create_session(db, admin, request)
    set_auth_cookies(response, access_token, refresh_token, csrf_token)
    security_logger.info("admin_login_success user_id=%s", admin.id)
    return AuthStatusResponse(authenticated=True, user=AuthUserRead(id=admin.id, email=admin.email, active=admin.active))


@router.post("/refresh", response_model=AuthStatusResponse)
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    rate_limit(request, "refresh", limit=30, window_seconds=300)
    refresh_token = request.cookies.get(REFRESH_COOKIE)
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    token_hash = hash_secret(refresh_token)
    result = await db.execute(select(AdminSession).where(AdminSession.refresh_token_hash == token_hash))
    session = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if not session or session.revoked_at or session.expires_at <= now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    admin = await db.get(AdminUser, session.user_id)
    if not admin or not admin.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    header_csrf = request.headers.get(CSRF_HEADER) or request.headers.get(CSRF_HEADER.title())
    cookie_csrf = request.cookies.get(CSRF_COOKIE)
    if not header_csrf or not cookie_csrf or header_csrf != cookie_csrf or not verify_secret(header_csrf, session.csrf_token_hash):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF validation failed")
    session.revoked_at = now
    access_token, next_refresh_token, next_csrf_token = await create_session(db, admin, request)
    set_auth_cookies(response, access_token, next_refresh_token, next_csrf_token)
    return AuthStatusResponse(authenticated=True, user=AuthUserRead(id=admin.id, email=admin.email, active=admin.active))


@router.get("/me", response_model=AuthStatusResponse)
async def me(admin: AdminUser = Depends(get_current_admin)):
    return AuthStatusResponse(authenticated=True, user=AuthUserRead(id=admin.id, email=admin.email, active=admin.active))


@router.post("/logout", response_model=AuthStatusResponse, dependencies=[Depends(validate_csrf)])
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    refresh_token = request.cookies.get(REFRESH_COOKIE)
    if refresh_token:
        result = await db.execute(select(AdminSession).where(AdminSession.refresh_token_hash == hash_secret(refresh_token)))
        session = result.scalar_one_or_none()
        if session and not session.revoked_at:
            session.revoked_at = datetime.now(timezone.utc)
            await db.commit()
            security_logger.info("admin_logout user_id=%s", session.user_id)
    clear_auth_cookies(response)
    return AuthStatusResponse(authenticated=False)
