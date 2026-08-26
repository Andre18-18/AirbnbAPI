from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.booking import BOOKING_STATUS_CONFIRMED, BOOKING_STATUS_PENDING, Booking
from backend.app.models.calendar import ExternalCalendarEvent
from backend.app.models.property import PropertyBlock
from backend.app.schemas.availability import AvailabilityResult

print("Hello")
def has_overlap(start_a, end_a, start_b, end_b) -> bool:
    return start_a < end_b and start_b < end_a


async def check_availability(db: AsyncSession, property_id: UUID, check_in, check_out) -> AvailabilityResult:
    now = datetime.now(timezone.utc)
    reasons: list[str] = []

    booking_rows = await db.execute(
        select(Booking).where(
            Booking.property_id == property_id,
            Booking.status_id.in_([BOOKING_STATUS_CONFIRMED, BOOKING_STATUS_PENDING]),
            Booking.check_in < check_out,
            Booking.check_out > check_in,
        )
    )
    for booking in booking_rows.scalars():
        if booking.status_id == BOOKING_STATUS_PENDING and booking.hold_expires_at and booking.hold_expires_at <= now:
            continue
        reasons.append(f"booking:{booking.source}")

    block_rows = await db.execute(
        select(PropertyBlock).where(
            PropertyBlock.property_id == property_id,
            PropertyBlock.start_date < check_out,
            PropertyBlock.end_date > check_in,
        )
    )
    if block_rows.scalars().first():
        reasons.append("manual_block")

    event_rows = await db.execute(
        select(ExternalCalendarEvent).where(
            ExternalCalendarEvent.property_id == property_id,
            ExternalCalendarEvent.start_date < check_out,
            ExternalCalendarEvent.end_date > check_in,
        )
    )
    if event_rows.scalars().first():
        reasons.append("external_calendar")

    return AvailabilityResult(
        property_id=property_id,
        check_in=check_in,
        check_out=check_out,
        available=not reasons,
        reasons=reasons,
    )
