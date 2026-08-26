from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.property import Property, PropertyPrice
from app.schemas.pricing import NightlyPrice, PriceQuote
from app.services.date_ranges import each_night


class PricingError(ValueError):
    pass


async def calculate_price(
    db: AsyncSession,
    property_id: UUID,
    check_in,
    check_out,
    number_of_guests: int,
) -> PriceQuote:
    property_obj = await db.get(Property, property_id)
    if not property_obj or not property_obj.active:
        raise PricingError("Property not found")
    if number_of_guests > property_obj.max_guests:
        raise PricingError("Too many guests for this property")

    nights = each_night(check_in, check_out)
    if len(nights) < property_obj.minimum_stay:
        raise PricingError("Stay is shorter than the property's minimum stay")

    overrides = await db.execute(
        select(PropertyPrice).where(PropertyPrice.property_id == property_id, PropertyPrice.date.in_(nights))
    )
    override_by_date = {row.date: row for row in overrides.scalars()}

    nightly_prices: list[NightlyPrice] = []
    subtotal = Decimal("0.00")
    for night in nights:
        override = override_by_date.get(night)
        price = override.nightly_price if override else property_obj.default_nightly_price
        nightly_prices.append(NightlyPrice(date=night, price=price))
        subtotal += price

    total = subtotal + property_obj.cleaning_fee
    return PriceQuote(
        property_id=property_id,
        check_in=check_in,
        check_out=check_out,
        nights=len(nights),
        nightly_prices=nightly_prices,
        subtotal=subtotal,
        cleaning_fee=property_obj.cleaning_fee,
        total=total,
    )
