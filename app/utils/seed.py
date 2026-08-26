import asyncio
from datetime import date, datetime, time, timezone
from decimal import Decimal

from sqlalchemy import delete, select

from app.core.config import get_settings
from app.core.security import hash_password, normalize_email, verify_password
from app.db.session import AsyncSessionLocal
from app.models.admin_user import USER_PROPERTY_ROLE_OWNER, AdminUser, UserProperty
from app.models.amenity import PropertyFeature, property_feature_links
from app.models.booking import (
    BOOKING_SOURCE_DIRECT,
    BOOKING_SOURCE_NAMES,
    BOOKING_STATUS_CONFIRMED,
    BOOKING_STATUS_NAMES,
    PAYMENT_STATUS_NAMES,
    PAYMENT_STATUS_PAID,
    Booking,
    BookingSource,
    BookingStatus,
    PaymentStatus,
)
from app.models.calendar import (
    CALENDAR_PROVIDER_AIRBNB,
    CALENDAR_PROVIDER_BOOKING,
    CALENDAR_PROVIDER_NAMES,
    CalendarProvider,
    CalendarSource,
    ExternalCalendarEvent,
)
from app.models.payment import PAYMENT_PROVIDER_NAMES, PaymentProvider
from app.models.property import Property, PropertyBlock, PropertyPhoto, PropertyPrice


async def ensure_lookup_rows(db, model, rows: dict[int, str]) -> None:
    existing = await db.execute(select(model).where(model.id.in_(rows.keys())))
    seen = {row.id for row in existing.scalars()}
    for row_id, name in rows.items():
        if row_id not in seen:
            db.add(model(id=row_id, name=name))
    await db.flush()


async def seed() -> None:
    settings = get_settings()
    async with AsyncSessionLocal() as db:
        await ensure_lookup_rows(db, BookingSource, BOOKING_SOURCE_NAMES)
        await ensure_lookup_rows(db, BookingStatus, BOOKING_STATUS_NAMES)
        await ensure_lookup_rows(db, PaymentStatus, PAYMENT_STATUS_NAMES)
        await ensure_lookup_rows(db, PaymentProvider, PAYMENT_PROVIDER_NAMES)
        await ensure_lookup_rows(db, CalendarProvider, CALENDAR_PROVIDER_NAMES)

        existing = await db.execute(select(Property).where(Property.slug.in_(["douros-heart-stay", "casa-da-portelinha"])))
        existing_property = existing.scalar_one_or_none()

        amenity_defs = [
            ("Wi-Fi", "wifi", "comfort"),
            ("Parking", "parking-circle", "practical"),
            ("Air conditioning", "snowflake", "comfort"),
            ("Kitchen", "chef-hat", "living"),
            ("Balcony", "landmark", "living"),
            ("Wine Museum nearby", "wine", "location"),
            ("Pet friendly on request", "heart", "practical"),
        ]
        amenity_names = [name for name, _icon, _category in amenity_defs]
        existing_amenities = await db.execute(select(PropertyFeature).where(PropertyFeature.name.in_(amenity_names)))
        amenity_by_name = {amenity.name: amenity for amenity in existing_amenities.scalars()}
        amenities = []
        for name, icon, category in amenity_defs:
            amenity = amenity_by_name.get(name)
            if not amenity:
                amenity = PropertyFeature(name=name, icon=icon, category=category)
                db.add(amenity)
            amenities.append(amenity)
        await db.flush()

        property_data = {
            "name": "Douro's Heart Stay",
            "slug": "douros-heart-stay",
            "short_description": "A bright apartment in the historic centre of Sao Joao da Pesqueira, close to the Wine Museum.",
            "description": "Discover the Douro from a comfortable apartment in Sao Joao da Pesqueira. The stay has two bedrooms, two bathrooms, a living room, balcony, air conditioning, Wi-Fi, parking, and a fully equipped kitchen with dishwasher and coffee machine. It is a practical base for wine country, viewpoints, river drives, and relaxed evenings in town.",
            "address": "Avenida Marques de Soveral 50 1FT",
            "city": "Sao Joao da Pesqueira",
            "country": "Portugal",
            "latitude": Decimal("41.147778"),
            "longitude": Decimal("-7.408163"),
            "max_guests": 6,
            "bedrooms": 2,
            "bathrooms": Decimal("2.0"),
            "check_in_time": time(15, 0),
            "check_out_time": time(11, 0),
            "default_nightly_price": Decimal("100.00"),
            "minimum_stay": 2,
            "cleaning_fee": Decimal("50.00"),
            "active": True,
        }
        photos = [
            "/images/682035686.jpg",
            "/images/682035576.jpg",
            "/images/682035800.jpg",
            "/images/682035968.jpg",
            "/images/682035527.jpg",
            "/images/682035558.jpg",
            "/images/682035564.jpg",
            "/images/682035585.jpg",
            "/images/682035598.jpg",
            "/images/682035622.jpg",
            "/images/682035648.jpg",
            "/images/682035661.jpg",
            "/images/682035670.jpg",
            "/images/682035694.jpg",
            "/images/682035707.jpg",
            "/images/682035713.jpg",
            "/images/682035723.jpg",
            "/images/682035750.jpg",
            "/images/682035767.jpg",
            "/images/682035777.jpg",
            "/images/682035789.jpg",
            "/images/682035842.jpg",
            "/images/682035848.jpg",
            "/images/682035851.jpg",
            "/images/682035858.jpg",
            "/images/682035871.jpg",
            "/images/682035884.jpg",
            "/images/682035897.jpg",
            "/images/682035914.jpg",
            "/images/682035925.jpg",
            "/images/682035935.jpg",
            "/images/682035949.jpg",
            "/images/682035955.jpg",
        ]

        admin_email = normalize_email(settings.admin_email)
        admin_result = await db.execute(select(AdminUser).where(AdminUser.email == admin_email))
        admin_user = admin_result.scalar_one_or_none()
        if not admin_user:
            admin_user = AdminUser(email=admin_email, password_hash=hash_password(settings.admin_password), active=True)
            db.add(admin_user)
            await db.flush()
        elif not admin_user.password_hash.startswith("$argon2") and verify_password(settings.admin_password, admin_user.password_hash):
            admin_user.password_hash = hash_password(settings.admin_password)

        if existing_property:
            property_obj = existing_property
            for key, value in property_data.items():
                setattr(property_obj, key, value)
            await db.execute(delete(PropertyPhoto).where(PropertyPhoto.property_id == property_obj.id))
            await db.execute(delete(property_feature_links).where(property_feature_links.c.property_id == property_obj.id))
            await db.flush()
            await db.execute(
                property_feature_links.insert(),
                [{"property_id": property_obj.id, "feature_id": amenity.id} for amenity in amenities],
            )
            for index, url in enumerate(photos):
                db.add(PropertyPhoto(property_id=property_obj.id, url=url, alt_text="Douro's Heart Stay", sort_order=index, is_cover=index == 0))
            await ensure_owner_role(db, admin_user.id, property_obj.id)
            await db.commit()
            return

        property_obj = Property(**property_data, amenities=amenities)
        db.add(property_obj)
        await db.flush()

        for index, url in enumerate(photos):
            db.add(PropertyPhoto(property_id=property_obj.id, url=url, alt_text="Douro's Heart Stay", sort_order=index, is_cover=index == 0))

        db.add_all(
            [
                PropertyPrice(property_id=property_obj.id, date=date(2026, 8, 15), nightly_price=Decimal("160.00"), minimum_stay=3),
                PropertyPrice(property_id=property_obj.id, date=date(2026, 8, 16), nightly_price=Decimal("160.00"), minimum_stay=3),
                PropertyPrice(property_id=property_obj.id, date=date(2026, 12, 24), nightly_price=Decimal("180.00"), minimum_stay=3),
                Booking(
                    property_id=property_obj.id,
                    source_id=BOOKING_SOURCE_DIRECT,
                    guest_name="Development Guest",
                    guest_email="guest@example.com",
                    check_in=date(2026, 9, 10),
                    check_out=date(2026, 9, 15),
                    number_of_guests=2,
                    nightly_subtotal=Decimal("500.00"),
                    cleaning_fee=Decimal("50.00"),
                    total_price=Decimal("550.00"),
                    status_id=BOOKING_STATUS_CONFIRMED,
                    payment_status_id=PAYMENT_STATUS_PAID,
                ),
                PropertyBlock(property_id=property_obj.id, start_date=date(2026, 10, 5), end_date=date(2026, 10, 8), reason="Maintenance"),
            ]
        )

        airbnb = CalendarSource(property_id=property_obj.id, provider_id=CALENDAR_PROVIDER_AIRBNB, import_url="https://example.com/airbnb.ics")
        booking = CalendarSource(property_id=property_obj.id, provider_id=CALENDAR_PROVIDER_BOOKING, import_url="https://example.com/booking.ics")
        db.add_all([airbnb, booking])
        await db.flush()
        db.add_all(
            [
                ExternalCalendarEvent(property_id=property_obj.id, calendar_source_id=airbnb.id, external_uid="airbnb-dev-1", start_date=date(2026, 9, 20), end_date=date(2026, 9, 23), summary="Airbnb reserved", last_seen_at=datetime.now(timezone.utc)),
                ExternalCalendarEvent(property_id=property_obj.id, calendar_source_id=booking.id, external_uid="booking-dev-1", start_date=date(2026, 11, 2), end_date=date(2026, 11, 6), summary="Booking.com reserved", last_seen_at=datetime.now(timezone.utc)),
            ]
        )
        await ensure_owner_role(db, admin_user.id, property_obj.id)
        await db.commit()


async def ensure_owner_role(db, user_id, property_id) -> None:
    existing = await db.execute(select(UserProperty).where(UserProperty.user_id == user_id, UserProperty.property_id == property_id))
    user_property = existing.scalar_one_or_none()
    if user_property:
        user_property.role = USER_PROPERTY_ROLE_OWNER
    else:
        db.add(UserProperty(user_id=user_id, property_id=property_id, role=USER_PROPERTY_ROLE_OWNER))


if __name__ == "__main__":
    asyncio.run(seed())
