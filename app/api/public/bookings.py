from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.booking import Booking
from app.schemas.booking import BookingCreate, BookingRead, BookingStatusRead, CheckoutResponse
from app.services.booking_service import BookingError, create_pending_booking
from app.services.stripe_service import StripeService
from app.core.logging import security_logger

router = APIRouter()


@router.post("/bookings", response_model=BookingRead, status_code=201)
async def create_booking(payload: BookingCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await create_pending_booking(db, payload)
    except BookingError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/bookings/{booking_id}/checkout", response_model=CheckoutResponse)
async def booking_checkout(booking_id: UUID, db: AsyncSession = Depends(get_db)):
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    checkout_url = StripeService().create_checkout_session_url(booking)
    return CheckoutResponse(checkout_url=checkout_url, booking_id=booking.id)


@router.get("/bookings/{booking_id}/status", response_model=BookingStatusRead)
async def booking_status(booking_id: UUID, db: AsyncSession = Depends(get_db)):
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
    db: AsyncSession = Depends(get_db),
):
    service = StripeService()
    try:
        payload = service.validate_webhook_payload(await request.body(), stripe_signature)
    except ValueError as exc:
        security_logger.warning("stripe_webhook_invalid error=%s", exc.__class__.__name__)
        raise HTTPException(status_code=400, detail="Invalid webhook") from exc
    event_type = payload.get("type")
    if event_type != "checkout.session.completed":
        return {"received": True}
    session = payload.get("data", {}).get("object", {})
    try:
        booking_id = UUID(session.get("metadata", {}).get("booking_id"))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Invalid webhook") from exc
    payment_id = session.get("payment_intent") or session.get("id")
    amount = Decimal(session.get("amount_total", 0)) / Decimal("100")
    currency = session.get("currency", "eur")
    await service.handle_checkout_completed(db, booking_id, payment_id, amount, currency)
    return {"received": True}
