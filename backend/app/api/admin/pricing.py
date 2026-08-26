from datetime import timedelta

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import authorized_property_ids, ensure_property_role, get_current_admin, validate_csrf
from backend.app.db.session import get_db
from backend.app.models.admin_user import USER_PROPERTY_ROLE_MANAGER, AdminUser
from backend.app.models.property import PropertyPrice
from backend.app.schemas.property import PriceOverrideUpsert

router = APIRouter(prefix="/admin/prices", dependencies=[Depends(validate_csrf)])


@router.get("")
async def list_prices(
    property_id: UUID | None = Query(default=None),
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    allowed = await authorized_property_ids(admin, db)
    if property_id:
        allowed = [property_id] if property_id in allowed else []
    result = await db.execute(select(PropertyPrice).where(PropertyPrice.property_id.in_(allowed)).order_by(PropertyPrice.date))
    return result.scalars().all()


@router.put("")
async def upsert_prices(
    payload: PriceOverrideUpsert,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    await ensure_property_role(admin, payload.property_id, USER_PROPERTY_ROLE_MANAGER, db)
    current = payload.start_date
    changed = 0
    while current < payload.end_date:
        await db.execute(delete(PropertyPrice).where(PropertyPrice.property_id == payload.property_id, PropertyPrice.date == current))
        if payload.nightly_price is not None:
            db.add(
                PropertyPrice(
                    property_id=payload.property_id,
                    date=current,
                    nightly_price=payload.nightly_price,
                    minimum_stay=payload.minimum_stay,
                )
            )
            changed += 1
        current += timedelta(days=1)
    await db.commit()
    return {"changed": changed}
