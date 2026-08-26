from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl


class CalendarSourceCreate(BaseModel):
    property_id: UUID
    provider: Literal["AIRBNB", "BOOKING", "VRBO", "OTHER"]
    import_url: HttpUrl
    export_enabled: bool = True
    active: bool = True
    model_config = ConfigDict(extra="forbid")


class CalendarSourceRead(BaseModel):
    id: UUID
    property_id: UUID
    provider: str
    import_url: str
    export_enabled: bool
    active: bool
    last_sync_at: datetime | None
    last_sync_status: str | None

    model_config = ConfigDict(from_attributes=True)
