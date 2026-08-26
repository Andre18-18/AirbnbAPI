from sqlalchemy import ForeignKey, String, Table, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import UUIDPrimaryKeyMixin

property_feature_links = Table(
    "property_feature_links",
    Base.metadata,
    Column("property_id", UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), primary_key=True),
    Column("feature_id", UUID(as_uuid=True), ForeignKey("property_features.id", ondelete="CASCADE"), primary_key=True),
)


class PropertyFeature(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "property_features"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    icon: Mapped[str | None] = mapped_column(String(80), nullable=True)
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)

    properties = relationship("Property", secondary=property_feature_links, back_populates="amenities")
