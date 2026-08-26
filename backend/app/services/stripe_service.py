from decimal import Decimal
from uuid import UUID

import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import get_settings
from backend.app.core.logging import security_logger
from backend.app.models.booking import BOOKING_STATUS_CONFIRMED, PAYMENT_STATUS_PAID, Booking
from backend.app.models.payment import PAYMENT_PROVIDER_STRIPE, Payment


class StripeService:
    def validate_webhook_payload(self, payload: bytes, signature: str | None) -> dict:
        settings = get_settings()
        if not settings.stripe_webhook_secret:
            import json

            return json.loads(payload.decode("utf-8"))
        if not signature:
            raise ValueError("Missing Stripe signature")
        return stripe.Webhook.construct_event(payload, signature, settings.stripe_webhook_secret)

    def create_checkout_session_url(self, booking: Booking) -> str:
        settings = get_settings()
        if not settings.stripe_secret_key:
            return f"{settings.frontend_url}/booking/success?booking_id={booking.id}&mock_checkout=true"
        return f"{settings.frontend_url}/booking/success?booking_id={booking.id}"

    async def handle_checkout_completed(
        self,
        db: AsyncSession,
        booking_id: UUID,
        external_payment_id: str,
        amount: Decimal,
        currency: str = "EUR",
    ) -> Booking:
        existing = await db.execute(
            select(Payment).where(
                Payment.provider_id == PAYMENT_PROVIDER_STRIPE,
                Payment.external_payment_id == external_payment_id,
            )
        )
        payment = existing.scalar_one_or_none()
        booking = await db.get(Booking, booking_id)
        if not booking:
            raise ValueError("Booking not found")
        if amount != booking.total_price or currency.upper() != "EUR":
            security_logger.warning("stripe_amount_mismatch booking_id=%s", booking.id)
            raise ValueError("Payment amount mismatch")
        if payment:
            return booking

        db.add(
            Payment(
                booking_id=booking.id,
                provider_id=PAYMENT_PROVIDER_STRIPE,
                external_payment_id=external_payment_id,
                amount=amount,
                currency=currency.upper(),
                status="PAID",
            )
        )
        booking.status_id = BOOKING_STATUS_CONFIRMED
        booking.payment_status_id = PAYMENT_STATUS_PAID
        booking.hold_expires_at = None
        await db.commit()
        await db.refresh(booking)
        return booking
