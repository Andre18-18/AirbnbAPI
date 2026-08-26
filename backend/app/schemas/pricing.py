from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class PriceQuoteRequest(BaseModel):
    property_id: UUID
    check_in: date
    check_out: date
    number_of_guests: int = Field(ge=1)

    @model_validator(mode="after")
    def validate_dates(self) -> "PriceQuoteRequest":
        if self.check_out <= self.check_in:
            raise ValueError("check_out must be after check_in")
        return self


class NightlyPrice(BaseModel):
    date: date
    price: Decimal


class PriceQuote(BaseModel):
    property_id: UUID
    check_in: date
    check_out: date
    nights: int
    nightly_prices: list[NightlyPrice]
    subtotal: Decimal
    cleaning_fee: Decimal
    total: Decimal
