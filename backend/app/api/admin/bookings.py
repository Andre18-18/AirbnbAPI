from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.dependencies import authorized_property_ids, ensure_property_role, get_current_admin, validate_csrf
from backend.app.db.session import get_db
from backend.app.models.admin_user import USER_PROPERTY_ROLE_MANAGER, USER_PROPERTY_ROLE_STAFF, AdminUser
from backend.app.models.booking import Booking
from backend.app.schemas.booking import BookingAdminUpdate, BookingRead, ManualBookingCreate
from backend.app.services.booking_service import BookingError, create_manual_booking

router = APIRouter(prefix="/admin/bookings", dependencies=[Depends(validate_csrf)])


@router.get("", response_model=list[BookingRead])
async def list_bookings(admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    allowed = await authorized_property_ids(admin, db)
    result = await db.execute(select(Booking).where(Booking.property_id.in_(allowed)).order_by(Booking.check_in.desc()))
    return result.scalars().all()


@router.get("/{booking_id}", response_model=BookingRead)
async def get_booking(booking_id: UUID, admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    await ensure_property_role(admin, booking.property_id, USER_PROPERTY_ROLE_STAFF, db)
    return booking


@router.post("", response_model=BookingRead, status_code=201)
async def manual_booking(payload: ManualBookingCreate, admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    try:
        await ensure_property_role(admin, payload.property_id, USER_PROPERTY_ROLE_MANAGER, db)
        return await create_manual_booking(db, payload)
    except BookingError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.put("/{booking_id}", response_model=BookingRead)
async def update_booking(booking_id: UUID, payload: BookingAdminUpdate, admin: AdminUser = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    await ensure_property_role(admin, booking.property_id, USER_PROPERTY_ROLE_MANAGER, db)
    for key, value in payload.model_dump().items():
        setattr(booking, key, value)
    await db.commit()
    await db.refresh(booking)
    return booking
