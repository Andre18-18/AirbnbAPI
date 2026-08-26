from datetime import date
from uuid import UUID

from pydantic import BaseModel


class AvailabilityResult(BaseModel):
    property_id: UUID
    check_in: date
    check_out: date
    available: bool
    reasons: list[str] = []
