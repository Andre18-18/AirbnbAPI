from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class BookingCreate(BaseModel):
    property_id: UUID
    guest_name: str = Field(min_length=2, max_length=180)
    guest_email: EmailStr
    guest_phone: str | None = Field(default=None, max_length=40, pattern=r"^[0-9 +().-]*$")
    check_in: date
    check_out: date
    number_of_guests: int = Field(ge=1, le=50)
    notes: str | None = Field(default=None, max_length=1000)
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_dates(self) -> "BookingCreate":
        if self.check_out <= self.check_in:
            raise ValueError("check_out must be after check_in")
        return self


class ManualBookingCreate(BookingCreate):
    source: Literal["DIRECT", "AIRBNB", "BOOKING", "MANUAL", "OTHER"] = "MANUAL"
    payment_status: Literal["NOT_REQUIRED", "PENDING", "PAID", "FAILED", "REFUNDED"] = "NOT_REQUIRED"
    model_config = ConfigDict(extra="forbid")


class BookingRead(BaseModel):
    id: UUID
    property_id: UUID
    source: str
    guest_name: str
    guest_email: str
    guest_phone: str | None
    check_in: date
    check_out: date
    number_of_guests: int
    nightly_subtotal: Decimal
    cleaning_fee: Decimal
    total_price: Decimal
    status: str
    payment_status: str
    hold_expires_at: datetime | None
    notes: str | None

    model_config = ConfigDict(from_attributes=True)


class BookingAdminUpdate(BaseModel):
    guest_name: str = Field(min_length=2, max_length=180)
    guest_email: EmailStr
    guest_phone: str | None = Field(default=None, max_length=40, pattern=r"^[0-9 +().-]*$")
    check_in: date
    check_out: date
    number_of_guests: int = Field(ge=1, le=50)
    notes: str | None = Field(default=None, max_length=1000)
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_dates(self) -> "BookingAdminUpdate":
        if self.check_out <= self.check_in:
            raise ValueError("check_out must be after check_in")
        return self


class CheckoutResponse(BaseModel):
    checkout_url: str
    booking_id: UUID


class BookingStatusRead(BaseModel):
    id: UUID
    status: str
    payment_status: str
    hold_expires_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
