from uuid import UUID

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.calendar_sync import build_property_ics

router = APIRouter()


@router.get("/calendar/{property_id}.ics")
async def export_calendar(property_id: UUID, db: AsyncSession = Depends(get_db)):
    return Response(await build_property_ics(db, property_id), media_type="text/calendar")
