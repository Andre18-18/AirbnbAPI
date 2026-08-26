from datetime import date, datetime
from decimal import Decimal
from builtins import property as builtin_property

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


BOOKING_SOURCE_DIRECT = 1
BOOKING_SOURCE_AIRBNB = 2
BOOKING_SOURCE_BOOKING = 3
BOOKING_SOURCE_MANUAL = 4
BOOKING_SOURCE_OTHER = 5

BOOKING_SOURCE_NAMES = {
    BOOKING_SOURCE_DIRECT: "DIRECT",
    BOOKING_SOURCE_AIRBNB: "AIRBNB",
    BOOKING_SOURCE_BOOKING: "BOOKING",
    BOOKING_SOURCE_MANUAL: "MANUAL",
    BOOKING_SOURCE_OTHER: "OTHER",
}
BOOKING_SOURCE_IDS = {name: source_id for source_id, name in BOOKING_SOURCE_NAMES.items()}


BOOKING_STATUS_PENDING = 1
BOOKING_STATUS_CONFIRMED = 2
BOOKING_STATUS_CANCELLED = 3
BOOKING_STATUS_EXPIRED = 4

BOOKING_STATUS_NAMES = {
    BOOKING_STATUS_PENDING: "PENDING",
    BOOKING_STATUS_CONFIRMED: "CONFIRMED",
    BOOKING_STATUS_CANCELLED: "CANCELLED",
    BOOKING_STATUS_EXPIRED: "EXPIRED",
}
BOOKING_STATUS_IDS = {name: status_id for status_id, name in BOOKING_STATUS_NAMES.items()}


PAYMENT_STATUS_NOT_REQUIRED = 1
PAYMENT_STATUS_PENDING = 2
PAYMENT_STATUS_PAID = 3
PAYMENT_STATUS_FAILED = 4
PAYMENT_STATUS_REFUNDED = 5

PAYMENT_STATUS_NAMES = {
    PAYMENT_STATUS_NOT_REQUIRED: "NOT_REQUIRED",
    PAYMENT_STATUS_PENDING: "PENDING",
    PAYMENT_STATUS_PAID: "PAID",
    PAYMENT_STATUS_FAILED: "FAILED",
    PAYMENT_STATUS_REFUNDED: "REFUNDED",
}
PAYMENT_STATUS_IDS = {name: status_id for status_id, name in PAYMENT_STATUS_NAMES.items()}


class BookingSource(Base):
    __tablename__ = "booking_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(40), unique=True)


class BookingStatus(Base):
    __tablename__ = "booking_statuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(40), unique=True)


class PaymentStatus(Base):
    __tablename__ = "payment_statuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(40), unique=True)


class Booking(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "bookings"
    __table_args__ = (
        Index("ix_bookings_property_dates", "property_id", "check_in", "check_out"),
        Index("ix_bookings_property_status", "property_id", "status_id"),
    )

    property_id = mapped_column(ForeignKey("properties.id", ondelete="RESTRICT"))
    source_id: Mapped[int] = mapped_column(ForeignKey("booking_sources.id"), default=BOOKING_SOURCE_DIRECT)
    external_reference: Mapped[str | None] = mapped_column(String(200), nullable=True)
    guest_name: Mapped[str] = mapped_column(String(180))
    guest_email: Mapped[str] = mapped_column(String(254))
    guest_phone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    check_in: Mapped[date] = mapped_column(Date)
    check_out: Mapped[date] = mapped_column(Date)
    number_of_guests: Mapped[int] = mapped_column(Integer)
    nightly_subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    cleaning_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status_id: Mapped[int] = mapped_column(ForeignKey("booking_statuses.id"), default=BOOKING_STATUS_PENDING)
    payment_status_id: Mapped[int] = mapped_column(ForeignKey("payment_statuses.id"), default=PAYMENT_STATUS_PENDING)
    hold_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    property = relationship("Property")
    payments = relationship("Payment", back_populates="booking", cascade="all, delete-orphan")
    source_ref = relationship("BookingSource")
    status_ref = relationship("BookingStatus")
    payment_status_ref = relationship("PaymentStatus")

    @builtin_property
    def source(self) -> str:
        source = self.__dict__.get("source_ref")
        return source.name if source else BOOKING_SOURCE_NAMES.get(self.source_id, "")

    @builtin_property
    def status(self) -> str:
        status = self.__dict__.get("status_ref")
        return status.name if status else BOOKING_STATUS_NAMES.get(self.status_id, "")

    @builtin_property
    def payment_status(self) -> str:
        payment_status = self.__dict__.get("payment_status_ref")
        return payment_status.name if payment_status else PAYMENT_STATUS_NAMES.get(self.payment_status_id, "")
