from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import authorized_property_ids, get_current_admin, require_min_role, validate_csrf
from app.db.session import get_db
from app.models.admin_user import USER_PROPERTY_ROLE_MANAGER, USER_PROPERTY_ROLE_OWNER, AdminUser, UserProperty
from app.models.property import Property
from app.schemas.property import PropertyCreateUpdate, PropertyRead

router = APIRouter(prefix="/admin/properties", dependencies=[Depends(validate_csrf)])


@router.get("", response_model=list[PropertyRead])
async def admin_properties(admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    property_ids = await authorized_property_ids(admin, db)
    result = await db.execute(
        select(Property)
        .where(Property.id.in_(property_ids))
        .options(selectinload(Property.photos), selectinload(Property.amenities))
    )
    return result.scalars().unique().all()


@router.post("", response_model=PropertyRead, status_code=201)
async def create_property(payload: PropertyCreateUpdate, admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    property_obj = Property(**payload.model_dump())
    db.add(property_obj)
    await db.flush()
    db.add(UserProperty(user_id=admin.id, property_id=property_obj.id, role=USER_PROPERTY_ROLE_OWNER))
    await db.commit()
    await db.refresh(property_obj)
    return property_obj


@router.put("/{property_id}", response_model=PropertyRead)
async def update_property(
    property_id: UUID,
    payload: PropertyCreateUpdate,
    _auth=Depends(require_min_role(USER_PROPERTY_ROLE_MANAGER)),
    db: AsyncSession = Depends(get_db),
):
    property_obj = await db.get(Property, property_id)
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    for key, value in payload.model_dump().items():
        setattr(property_obj, key, value)
    await db.commit()
    await db.refresh(property_obj)
    return property_obj
