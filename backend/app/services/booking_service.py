from datetime import datetime, timedelta, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import get_settings
from backend.app.models.booking import (
    BOOKING_SOURCE_DIRECT,
    BOOKING_SOURCE_IDS,
    BOOKING_STATUS_CONFIRMED,
    BOOKING_STATUS_PENDING,
    PAYMENT_STATUS_IDS,
    PAYMENT_STATUS_PENDING,
    Booking,
)
from backend.app.schemas.booking import BookingCreate, ManualBookingCreate
from backend.app.services.availability import check_availability
from backend.app.services.pricing import calculate_price


class BookingError(ValueError):
    pass


async def create_pending_booking(db: AsyncSession, payload: BookingCreate) -> Booking:
    await db.execute(text("select pg_advisory_xact_lock(hashtext(:lock_key))"), {"lock_key": str(payload.property_id)})
    availability = await check_availability(db, payload.property_id, payload.check_in, payload.check_out)
    if not availability.available:
        raise BookingError("Selected dates are unavailable")

    quote = await calculate_price(db, payload.property_id, payload.check_in, payload.check_out, payload.number_of_guests)
    settings = get_settings()
    booking = Booking(
        property_id=payload.property_id,
        source_id=BOOKING_SOURCE_DIRECT,
        guest_name=payload.guest_name,
        guest_email=str(payload.guest_email),
        guest_phone=payload.guest_phone,
        check_in=payload.check_in,
        check_out=payload.check_out,
        number_of_guests=payload.number_of_guests,
        nightly_subtotal=quote.subtotal,
        cleaning_fee=quote.cleaning_fee,
        total_price=quote.total,
        status_id=BOOKING_STATUS_PENDING,
        payment_status_id=PAYMENT_STATUS_PENDING,
        hold_expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.booking_hold_minutes),
        notes=payload.notes,
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking


async def create_manual_booking(db: AsyncSession, payload: ManualBookingCreate) -> Booking:
    await db.execute(text("select pg_advisory_xact_lock(hashtext(:lock_key))"), {"lock_key": str(payload.property_id)})
    availability = await check_availability(db, payload.property_id, payload.check_in, payload.check_out)
    if not availability.available:
        raise BookingError("Selected dates are unavailable")
    quote = await calculate_price(db, payload.property_id, payload.check_in, payload.check_out, payload.number_of_guests)
    booking = Booking(
        property_id=payload.property_id,
        source_id=BOOKING_SOURCE_IDS[payload.source],
        guest_name=payload.guest_name,
        guest_email=str(payload.guest_email),
        guest_phone=payload.guest_phone,
        check_in=payload.check_in,
        check_out=payload.check_out,
        number_of_guests=payload.number_of_guests,
        nightly_subtotal=quote.subtotal,
        cleaning_fee=quote.cleaning_fee,
        total_price=quote.total,
        status_id=BOOKING_STATUS_CONFIRMED,
        payment_status_id=PAYMENT_STATUS_IDS[payload.payment_status],
        notes=payload.notes,
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking
