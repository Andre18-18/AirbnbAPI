from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import authorized_property_ids, ensure_property_role, get_current_admin, validate_csrf
from app.db.session import get_db
from app.models.admin_user import USER_PROPERTY_ROLE_MANAGER, AdminUser
from app.models.calendar import CALENDAR_PROVIDER_IDS, CalendarSource
from app.models.property import PropertyBlock
from app.schemas.calendar import CalendarSourceCreate, CalendarSourceRead
from app.schemas.property import PropertyBlockCreate
from app.services.calendar_sync import sync_calendar_source

router = APIRouter(prefix="/admin", dependencies=[Depends(validate_csrf)])


@router.post("/blocks", status_code=201)
async def create_block(
    payload: PropertyBlockCreate,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    await ensure_property_role(admin, payload.property_id, USER_PROPERTY_ROLE_MANAGER, db)
    block = PropertyBlock(**payload.model_dump(), created_at=datetime.now(timezone.utc))
    db.add(block)
    await db.commit()
    return {"id": block.id}


@router.delete("/blocks/{block_id}", status_code=204)
async def delete_block(block_id: UUID, admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    block = await db.get(PropertyBlock, block_id)
    if block:
        allowed = await authorized_property_ids(admin, db)
        if block.property_id not in allowed:
            raise HTTPException(status_code=403, detail="Not authorized for this property")
        await db.delete(block)
        await db.commit()


@router.get("/calendar-sources", response_model=list[CalendarSourceRead])
async def list_calendar_sources(admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    allowed = await authorized_property_ids(admin, db)
    result = await db.execute(select(CalendarSource).where(CalendarSource.property_id.in_(allowed)))
    return result.scalars().all()


@router.post("/calendar-sources", response_model=CalendarSourceRead, status_code=201)
async def create_calendar_source(
    payload: CalendarSourceCreate,
    admin: AdminUser = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    await ensure_property_role(admin, payload.property_id, USER_PROPERTY_ROLE_MANAGER, db)
    data = payload.model_dump()
    provider = data.pop("provider")
    data["import_url"] = str(data["import_url"])
    source = CalendarSource(**data, provider_id=CALENDAR_PROVIDER_IDS[provider])
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


@router.post("/calendar-sources/{source_id}/sync", response_model=CalendarSourceRead)
async def sync_calendar(source_id: UUID, admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    source = await db.get(CalendarSource, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Calendar source not found")
    allowed = await authorized_property_ids(admin, db)
    if source.property_id not in allowed:
        raise HTTPException(status_code=403, detail="Not authorized for this property")
    return await sync_calendar_source(db, source)
