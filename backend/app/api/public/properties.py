from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.db.session import get_db
from backend.app.models.property import Property
from backend.app.schemas.availability import AvailabilityResult
from backend.app.schemas.pricing import PriceQuote
from backend.app.schemas.property import PropertyRead, PropertySummary
from backend.app.services.availability import check_availability
from backend.app.services.calendar_sync import build_property_ics
from backend.app.services.pricing import PricingError, calculate_price

router = APIRouter()


@router.get("/properties", response_model=list[PropertySummary])
async def list_properties(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Property)
        .where(Property.active.is_(True))
        .options(selectinload(Property.photos))
        .order_by(Property.name)
    )
    summaries: list[PropertySummary] = []
    for property_obj in result.scalars().unique():
        cover = next((photo for photo in property_obj.photos if photo.is_cover), None)
        cover = cover or (property_obj.photos[0] if property_obj.photos else None)
        summaries.append(
            PropertySummary(
                id=property_obj.id,
                name=property_obj.name,
                slug=property_obj.slug,
                short_description=property_obj.short_description,
                city=property_obj.city,
                country=property_obj.country,
                max_guests=property_obj.max_guests,
                bedrooms=property_obj.bedrooms,
                bathrooms=property_obj.bathrooms,
                default_nightly_price=property_obj.default_nightly_price,
                cover_photo_url=cover.url if cover else None,
            )
        )
    return summaries


@router.get("/properties/{slug}", response_model=PropertyRead)
async def get_property(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Property)
        .where(Property.slug == slug, Property.active.is_(True))
        .options(selectinload(Property.photos), selectinload(Property.amenities))
    )
    property_obj = result.scalars().unique().one_or_none()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    property_obj.photos.sort(key=lambda photo: photo.sort_order)
    return property_obj


@router.get("/properties/{property_id}/availability", response_model=AvailabilityResult)
async def property_availability(property_id: UUID, check_in: date, check_out: date, db: AsyncSession = Depends(get_db)):
    if check_out <= check_in:
        raise HTTPException(status_code=422, detail="check_out must be after check_in")
    return await check_availability(db, property_id, check_in, check_out)


@router.get("/properties/{property_id}/pricing", response_model=PriceQuote)
async def property_pricing(
    property_id: UUID,
    check_in: date,
    check_out: date,
    guests: int = 1,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await calculate_price(db, property_id, check_in, check_out, guests)
    except PricingError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/properties/{property_id}/calendar")
async def property_calendar_alias(property_id: UUID, db: AsyncSession = Depends(get_db)):
    return Response(await build_property_ics(db, property_id), media_type="text/calendar")
