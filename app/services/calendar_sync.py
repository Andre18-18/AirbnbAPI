from datetime import datetime, timezone
import ipaddress
import socket
from urllib.parse import urlparse
from uuid import UUID

import httpx
from icalendar import Calendar, Event
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import BOOKING_SOURCE_DIRECT, BOOKING_SOURCE_MANUAL, BOOKING_STATUS_CONFIRMED, Booking
from app.models.calendar import CalendarSource, ExternalCalendarEvent
from app.core.config import get_settings
from app.core.logging import security_logger


BLOCKED_HOSTS = {"localhost", "metadata.google.internal"}


def validate_public_ical_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Invalid calendar URL")
    hostname = parsed.hostname.lower()
    if hostname in BLOCKED_HOSTS or hostname.endswith(".local"):
        raise ValueError("Calendar URL host is not allowed")
    for family, _type, _proto, _canonname, sockaddr in socket.getaddrinfo(hostname, parsed.port or 443):
        ip = ipaddress.ip_address(sockaddr[0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise ValueError("Calendar URL resolves to a non-public address")


def _event_dates(event: Event):
    start = event.decoded("DTSTART")
    end = event.decoded("DTEND")
    return start.date() if hasattr(start, "date") else start, end.date() if hasattr(end, "date") else end


async def sync_calendar_source(db: AsyncSession, source: CalendarSource) -> CalendarSource:
    seen: set[str] = set()
    try:
        validate_public_ical_url(source.import_url)
        settings = get_settings()
        async with httpx.AsyncClient(timeout=20, follow_redirects=False) as client:
            response = await client.get(source.import_url)
            response.raise_for_status()
        content = await response.aread()
        if len(content) > settings.max_ical_bytes:
            raise ValueError("Calendar response is too large")
        calendar = Calendar.from_ical(content)
        for component in calendar.walk("VEVENT"):
            uid = str(component.get("UID"))
            start_date, end_date = _event_dates(component)
            summary = str(component.get("SUMMARY", "Reserved"))
            seen.add(uid)
            existing = await db.execute(
                select(ExternalCalendarEvent).where(
                    ExternalCalendarEvent.calendar_source_id == source.id,
                    ExternalCalendarEvent.external_uid == uid,
                )
            )
            event = existing.scalar_one_or_none()
            if event:
                event.start_date = start_date
                event.end_date = end_date
                event.summary = summary
                event.last_seen_at = datetime.now(timezone.utc)
            else:
                db.add(
                    ExternalCalendarEvent(
                        property_id=source.property_id,
                        calendar_source_id=source.id,
                        external_uid=uid,
                        start_date=start_date,
                        end_date=end_date,
                        summary=summary,
                        last_seen_at=datetime.now(timezone.utc),
                    )
                )
        source.last_sync_status = f"OK: {len(seen)} events"
    except Exception as exc:
        security_logger.warning("ical_sync_failed source_id=%s error=%s", source.id, exc.__class__.__name__)
        source.last_sync_status = f"ERROR: {exc.__class__.__name__}"
    source.last_sync_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(source)
    return source


async def build_property_ics(db: AsyncSession, property_id: UUID) -> str:
    calendar = Calendar()
    calendar.add("prodid", "-//Vacation Rental//Booking Calendar//EN")
    calendar.add("version", "2.0")
    rows = await db.execute(
        select(Booking).where(
            Booking.property_id == property_id,
            Booking.status_id == BOOKING_STATUS_CONFIRMED,
            Booking.source_id.in_([BOOKING_SOURCE_DIRECT, BOOKING_SOURCE_MANUAL]),
        )
    )
    for booking in rows.scalars():
        event = Event()
        event.add("uid", f"{booking.id}@vacation-rental")
        event.add("summary", "Reserved")
        event.add("dtstart", booking.check_in)
        event.add("dtend", booking.check_out)
        calendar.add_component(event)
    return calendar.to_ical().decode("utf-8")
