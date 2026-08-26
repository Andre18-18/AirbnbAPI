from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


PAYMENT_PROVIDER_STRIPE = 1
PAYMENT_PROVIDER_NAMES = {PAYMENT_PROVIDER_STRIPE: "STRIPE"}
PAYMENT_PROVIDER_IDS = {name: provider_id for provider_id, name in PAYMENT_PROVIDER_NAMES.items()}


class PaymentProvider(Base):
    __tablename__ = "payment_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(40), unique=True)


class Payment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint("provider_id", "external_payment_id", name="uq_payment_provider_external_id"),
        Index("ix_payments_booking", "booking_id"),
    )

    booking_id = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"))
    provider_id: Mapped[int] = mapped_column(ForeignKey("payment_providers.id"))
    external_payment_id: Mapped[str] = mapped_column(String(240))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    status: Mapped[str] = mapped_column(String(80))

    booking = relationship("Booking", back_populates="payments")
    provider_ref = relationship("PaymentProvider")

    @property
    def provider(self) -> str:
        provider = self.__dict__.get("provider_ref")
        return provider.name if provider else PAYMENT_PROVIDER_NAMES.get(self.provider_id, "")
