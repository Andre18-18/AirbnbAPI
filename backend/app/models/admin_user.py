from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class AdminUser(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "admin_users"

    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    sessions = relationship("AdminSession", back_populates="user", cascade="all, delete-orphan")
    property_roles = relationship("UserProperty", back_populates="user", cascade="all, delete-orphan")


class AdminSession(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "admin_sessions"
    __table_args__ = (
        Index("ix_admin_sessions_user_active", "user_id", "revoked_at"),
        Index("ix_admin_sessions_refresh_token_hash", "refresh_token_hash"),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("admin_users.id", ondelete="CASCADE"))
    refresh_token_hash: Mapped[str] = mapped_column(String(128), unique=True)
    csrf_token_hash: Mapped[str] = mapped_column(String(128))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(300), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(80), nullable=True)

    user = relationship("AdminUser", back_populates="sessions")


USER_PROPERTY_ROLE_OWNER = "OWNER"
USER_PROPERTY_ROLE_MANAGER = "MANAGER"
USER_PROPERTY_ROLE_STAFF = "STAFF"


class UserProperty(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "user_properties"
    __table_args__ = (UniqueConstraint("user_id", "property_id", name="uq_user_property"),)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("admin_users.id", ondelete="CASCADE"))
    property_id: Mapped[UUID] = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(20))

    user = relationship("AdminUser", back_populates="property_roles")
