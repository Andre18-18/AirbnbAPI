from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


CALENDAR_PROVIDER_AIRBNB = 1
CALENDAR_PROVIDER_BOOKING = 2
CALENDAR_PROVIDER_VRBO = 3
CALENDAR_PROVIDER_OTHER = 4

CALENDAR_PROVIDER_NAMES = {
    CALENDAR_PROVIDER_AIRBNB: "AIRBNB",
    CALENDAR_PROVIDER_BOOKING: "BOOKING",
    CALENDAR_PROVIDER_VRBO: "VRBO",
    CALENDAR_PROVIDER_OTHER: "OTHER",
}
CALENDAR_PROVIDER_IDS = {name: provider_id for provider_id, name in CALENDAR_PROVIDER_NAMES.items()}


class CalendarProvider(Base):
    __tablename__ = "calendar_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(40), unique=True)


class CalendarSource(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "calendar_sources"

    property_id = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"), index=True)
    provider_id: Mapped[int] = mapped_column(ForeignKey("calendar_providers.id"))
    import_url: Mapped[str] = mapped_column(String(1000))
    export_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sync_status: Mapped[str | None] = mapped_column(String(300), nullable=True)

    events = relationship("ExternalCalendarEvent", back_populates="calendar_source", cascade="all, delete-orphan")
    provider_ref = relationship("CalendarProvider")

    @property
    def provider(self) -> str:
        provider = self.__dict__.get("provider_ref")
        return provider.name if provider else CALENDAR_PROVIDER_NAMES.get(self.provider_id, "")


class ExternalCalendarEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "external_calendar_events"
    __table_args__ = (
        UniqueConstraint("calendar_source_id", "external_uid", name="uq_external_calendar_event_source_uid"),
        Index("ix_external_events_property_dates", "property_id", "start_date", "end_date"),
    )

    property_id = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"))
    calendar_source_id = mapped_column(ForeignKey("calendar_sources.id", ondelete="CASCADE"))
    external_uid: Mapped[str] = mapped_column(String(300))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    summary: Mapped[str | None] = mapped_column(String(300), nullable=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    calendar_source = relationship("CalendarSource", back_populates="events")
