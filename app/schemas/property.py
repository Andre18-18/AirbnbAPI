from datetime import date, time
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class PropertyFeatureRead(BaseModel):
    id: UUID
    name: str
    icon: str | None = None
    category: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PropertyPhotoRead(BaseModel):
    id: UUID
    url: str
    alt_text: str | None = None
    sort_order: int
    is_cover: bool

    model_config = ConfigDict(from_attributes=True)


class PropertyRead(BaseModel):
    id: UUID
    name: str
    slug: str
    short_description: str
    description: str
    address: str | None = None
    city: str | None = None
    country: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    max_guests: int
    bedrooms: int
    bathrooms: Decimal
    check_in_time: time
    check_out_time: time
    default_nightly_price: Decimal
    minimum_stay: int
    cleaning_fee: Decimal
    active: bool
    photos: list[PropertyPhotoRead] = []
    amenities: list[PropertyFeatureRead] = []

    model_config = ConfigDict(from_attributes=True)


class PropertySummary(BaseModel):
    id: UUID
    name: str
    slug: str
    short_description: str
    city: str | None = None
    country: str | None = None
    max_guests: int
    bedrooms: int
    bathrooms: Decimal
    default_nightly_price: Decimal
    cover_photo_url: str | None = None


class PropertyCreateUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    slug: str = Field(min_length=2, max_length=180, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    short_description: str = Field(min_length=10, max_length=300)
    description: str = Field(min_length=20, max_length=5000)
    address: str | None = Field(default=None, max_length=240)
    city: str | None = Field(default=None, max_length=120)
    country: str | None = Field(default=None, max_length=120)
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    max_guests: int = Field(ge=1, le=50)
    bedrooms: int = Field(ge=0, le=20)
    bathrooms: Decimal = Field(ge=0, le=20)
    check_in_time: time
    check_out_time: time
    default_nightly_price: Decimal = Field(ge=0, le=10000)
    minimum_stay: int = Field(ge=1, le=365)
    cleaning_fee: Decimal = Field(ge=0, le=5000)
    active: bool = True
    model_config = ConfigDict(extra="forbid")


class PriceOverrideUpsert(BaseModel):
    property_id: UUID
    start_date: date
    end_date: date
    nightly_price: Decimal | None = Field(default=None, ge=0, le=10000)
    minimum_stay: int | None = Field(default=None, ge=1, le=365)
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_dates(self) -> "PriceOverrideUpsert":
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        if (self.end_date - self.start_date).days > 370:
            raise ValueError("price update range is too large")
        return self


class PropertyBlockCreate(BaseModel):
    property_id: UUID
    start_date: date
    end_date: date
    reason: str | None = Field(default=None, max_length=200)
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def validate_dates(self) -> "PropertyBlockCreate":
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self
