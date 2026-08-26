from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.logging import security_logger
from backend.app.core.security import decode_access_token, hash_secret, verify_secret
from backend.app.db.session import get_db
from backend.app.models.admin_user import (
    USER_PROPERTY_ROLE_MANAGER,
    USER_PROPERTY_ROLE_OWNER,
    USER_PROPERTY_ROLE_STAFF,
    AdminSession,
    AdminUser,
    UserProperty,
)

ACCESS_COOKIE = "admin_access_token"
CSRF_COOKIE = "XSRF-TOKEN"
CSRF_HEADER = "x-csrf-token"

ROLE_RANK = {
    USER_PROPERTY_ROLE_STAFF: 1,
    USER_PROPERTY_ROLE_MANAGER: 2,
    USER_PROPERTY_ROLE_OWNER: 3,
}


@dataclass(frozen=True)
class PropertyAuthorization:
    user: AdminUser
    property_id: UUID
    role: str


async def get_current_session(request: Request, db: AsyncSession) -> tuple[AdminUser, AdminSession]:
    token = request.cookies.get(ACCESS_COOKIE)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        admin_id, session_id = decode_access_token(token)
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required") from None
    session = await db.get(AdminSession, session_id)
    admin = await db.get(AdminUser, admin_id)
    now = datetime.now(timezone.utc)
    if not session or session.user_id != admin_id or session.revoked_at or session.expires_at <= now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    if not admin or not admin.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return admin, session


async def get_current_admin(request: Request, db: AsyncSession = Depends(get_db)) -> AdminUser:
    admin, _session = await get_current_session(request, db)
    return admin


async def validate_csrf(request: Request, db: AsyncSession = Depends(get_db)) -> None:
    if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
        return
    _admin, session = await get_current_session(request, db)
    header_token = request.headers.get(CSRF_HEADER) or request.headers.get(CSRF_HEADER.title())
    cookie_token = request.cookies.get(CSRF_COOKIE)
    if not header_token or not cookie_token or header_token != cookie_token or not verify_secret(header_token, session.csrf_token_hash):
        security_logger.warning("csrf_validation_failed path=%s", request.url.path)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF validation failed")


def require_min_role(min_role: str):
    async def dependency(
        property_id: UUID,
        admin: AdminUser = Depends(get_current_admin),
        db: AsyncSession = Depends(get_db),
    ) -> PropertyAuthorization:
        result = await db.execute(
            select(UserProperty).where(UserProperty.user_id == admin.id, UserProperty.property_id == property_id)
        )
        access = result.scalar_one_or_none()
        if not access or ROLE_RANK.get(access.role, 0) < ROLE_RANK[min_role]:
            security_logger.warning("property_authorization_denied user_id=%s property_id=%s", admin.id, property_id)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this property")
        return PropertyAuthorization(user=admin, property_id=property_id, role=access.role)

    return dependency


async def authorized_property_ids(admin: AdminUser, db: AsyncSession) -> list[UUID]:
    result = await db.execute(select(UserProperty.property_id).where(UserProperty.user_id == admin.id))
    return list(result.scalars().all())


async def ensure_property_role(admin: AdminUser, property_id: UUID, min_role: str, db: AsyncSession) -> PropertyAuthorization:
    result = await db.execute(select(UserProperty).where(UserProperty.user_id == admin.id, UserProperty.property_id == property_id))
    access = result.scalar_one_or_none()
    if not access or ROLE_RANK.get(access.role, 0) < ROLE_RANK[min_role]:
        security_logger.warning("property_authorization_denied user_id=%s property_id=%s", admin.id, property_id)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this property")
    return PropertyAuthorization(user=admin, property_id=property_id, role=access.role)
