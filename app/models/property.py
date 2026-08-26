from datetime import date, datetime, time, timezone
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Property(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "properties"

    name: Mapped[str] = mapped_column(String(160))
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    short_description: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text)
    address: Mapped[str | None] = mapped_column(String(240), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    max_guests: Mapped[int] = mapped_column(Integer)
    bedrooms: Mapped[int] = mapped_column(Integer)
    bathrooms: Mapped[Decimal] = mapped_column(Numeric(3, 1))
    check_in_time: Mapped[time] = mapped_column(Time)
    check_out_time: Mapped[time] = mapped_column(Time)
    default_nightly_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    minimum_stay: Mapped[int] = mapped_column(Integer, default=1)
    cleaning_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    photos = relationship("PropertyPhoto", back_populates="property", cascade="all, delete-orphan")
    amenities = relationship("PropertyFeature", secondary="property_feature_links", back_populates="properties")
    prices = relationship("PropertyPrice", back_populates="property", cascade="all, delete-orphan")
    blocks = relationship("PropertyBlock", back_populates="property", cascade="all, delete-orphan")


class PropertyPhoto(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "property_photos"

    property_id = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"), index=True)
    url: Mapped[str] = mapped_column(String(500))
    alt_text: Mapped[str | None] = mapped_column(String(200), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_cover: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    property = relationship("Property", back_populates="photos")


class PropertyPrice(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "property_prices"
    __table_args__ = (
        UniqueConstraint("property_id", "date", name="uq_property_price_date"),
        Index("ix_property_prices_property_date", "property_id", "date"),
    )

    property_id = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"))
    date: Mapped[date] = mapped_column(Date)
    nightly_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    minimum_stay: Mapped[int | None] = mapped_column(Integer, nullable=True)

    property = relationship("Property", back_populates="prices")


class PropertyBlock(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "property_blocks"
    __table_args__ = (Index("ix_property_blocks_property_dates", "property_id", "start_date", "end_date"),)

    property_id = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    reason: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    property = relationship("Property", back_populates="blocks")
