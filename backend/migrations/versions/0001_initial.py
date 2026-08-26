"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-10
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("booking_sources", sa.Column("id", sa.Integer(), nullable=False), sa.Column("name", sa.String(40), nullable=False), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("name"))
    op.create_table("booking_statuses", sa.Column("id", sa.Integer(), nullable=False), sa.Column("name", sa.String(40), nullable=False), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("name"))
    op.create_table("payment_statuses", sa.Column("id", sa.Integer(), nullable=False), sa.Column("name", sa.String(40), nullable=False), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("name"))
    op.create_table("payment_providers", sa.Column("id", sa.Integer(), nullable=False), sa.Column("name", sa.String(40), nullable=False), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("name"))
    op.create_table("calendar_providers", sa.Column("id", sa.Integer(), nullable=False), sa.Column("name", sa.String(40), nullable=False), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("name"))

    op.bulk_insert(sa.table("booking_sources", sa.column("id", sa.Integer), sa.column("name", sa.String)), [{"id": 1, "name": "DIRECT"}, {"id": 2, "name": "AIRBNB"}, {"id": 3, "name": "BOOKING"}, {"id": 4, "name": "MANUAL"}, {"id": 5, "name": "OTHER"}])
    op.bulk_insert(sa.table("booking_statuses", sa.column("id", sa.Integer), sa.column("name", sa.String)), [{"id": 1, "name": "PENDING"}, {"id": 2, "name": "CONFIRMED"}, {"id": 3, "name": "CANCELLED"}, {"id": 4, "name": "EXPIRED"}])
    op.bulk_insert(sa.table("payment_statuses", sa.column("id", sa.Integer), sa.column("name", sa.String)), [{"id": 1, "name": "NOT_REQUIRED"}, {"id": 2, "name": "PENDING"}, {"id": 3, "name": "PAID"}, {"id": 4, "name": "FAILED"}, {"id": 5, "name": "REFUNDED"}])
    op.bulk_insert(sa.table("payment_providers", sa.column("id", sa.Integer), sa.column("name", sa.String)), [{"id": 1, "name": "STRIPE"}])
    op.bulk_insert(sa.table("calendar_providers", sa.column("id", sa.Integer), sa.column("name", sa.String)), [{"id": 1, "name": "AIRBNB"}, {"id": 2, "name": "BOOKING"}, {"id": 3, "name": "VRBO"}, {"id": 4, "name": "OTHER"}])

    op.create_table("admin_users", sa.Column("email", sa.String(254), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("active", sa.Boolean(), nullable=False), sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_admin_users_email"), "admin_users", ["email"], unique=True)
    op.create_table("property_features", sa.Column("name", sa.String(100), nullable=False), sa.Column("icon", sa.String(80), nullable=True), sa.Column("category", sa.String(80), nullable=True), sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_property_features_name"), "property_features", ["name"], unique=True)
    op.create_table("properties", sa.Column("name", sa.String(160), nullable=False), sa.Column("slug", sa.String(180), nullable=False), sa.Column("short_description", sa.String(300), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("address", sa.String(240), nullable=True), sa.Column("city", sa.String(120), nullable=True), sa.Column("country", sa.String(120), nullable=True), sa.Column("latitude", sa.Numeric(9, 6), nullable=True), sa.Column("longitude", sa.Numeric(9, 6), nullable=True), sa.Column("max_guests", sa.Integer(), nullable=False), sa.Column("bedrooms", sa.Integer(), nullable=False), sa.Column("bathrooms", sa.Numeric(3, 1), nullable=False), sa.Column("check_in_time", sa.Time(), nullable=False), sa.Column("check_out_time", sa.Time(), nullable=False), sa.Column("default_nightly_price", sa.Numeric(10, 2), nullable=False), sa.Column("minimum_stay", sa.Integer(), nullable=False), sa.Column("cleaning_fee", sa.Numeric(10, 2), nullable=False), sa.Column("active", sa.Boolean(), nullable=False), sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_properties_active"), "properties", ["active"], unique=False)
    op.create_index(op.f("ix_properties_slug"), "properties", ["slug"], unique=True)
    op.create_table("bookings", sa.Column("property_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("source_id", sa.Integer(), nullable=False), sa.Column("external_reference", sa.String(200), nullable=True), sa.Column("guest_name", sa.String(180), nullable=False), sa.Column("guest_email", sa.String(254), nullable=False), sa.Column("guest_phone", sa.String(80), nullable=True), sa.Column("check_in", sa.Date(), nullable=False), sa.Column("check_out", sa.Date(), nullable=False), sa.Column("number_of_guests", sa.Integer(), nullable=False), sa.Column("nightly_subtotal", sa.Numeric(10, 2), nullable=False), sa.Column("cleaning_fee", sa.Numeric(10, 2), nullable=False), sa.Column("total_price", sa.Numeric(10, 2), nullable=False), sa.Column("status_id", sa.Integer(), nullable=False), sa.Column("payment_status_id", sa.Integer(), nullable=False), sa.Column("hold_expires_at", sa.DateTime(timezone=True), nullable=True), sa.Column("notes", sa.Text(), nullable=True), sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.ForeignKeyConstraint(["payment_status_id"], ["payment_statuses.id"]), sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="RESTRICT"), sa.ForeignKeyConstraint(["source_id"], ["booking_sources.id"]), sa.ForeignKeyConstraint(["status_id"], ["booking_statuses.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_bookings_property_dates", "bookings", ["property_id", "check_in", "check_out"], unique=False)
    op.create_index("ix_bookings_property_status", "bookings", ["property_id", "status_id"], unique=False)
    op.create_index(op.f("ix_bookings_hold_expires_at"), "bookings", ["hold_expires_at"], unique=False)
    op.create_table("calendar_sources", sa.Column("property_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("provider_id", sa.Integer(), nullable=False), sa.Column("import_url", sa.String(1000), nullable=False), sa.Column("export_enabled", sa.Boolean(), nullable=False), sa.Column("active", sa.Boolean(), nullable=False), sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True), sa.Column("last_sync_status", sa.String(300), nullable=True), sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["provider_id"], ["calendar_providers.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_calendar_sources_property_id"), "calendar_sources", ["property_id"], unique=False)
    op.create_table("property_feature_links", sa.Column("property_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("feature_id", postgresql.UUID(as_uuid=True), nullable=False), sa.ForeignKeyConstraint(["feature_id"], ["property_features.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("property_id", "feature_id"))
    op.create_table("property_blocks", sa.Column("property_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("start_date", sa.Date(), nullable=False), sa.Column("end_date", sa.Date(), nullable=False), sa.Column("reason", sa.String(200), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_property_blocks_property_dates", "property_blocks", ["property_id", "start_date", "end_date"], unique=False)
    op.create_table("property_photos", sa.Column("property_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("url", sa.String(500), nullable=False), sa.Column("alt_text", sa.String(200), nullable=True), sa.Column("sort_order", sa.Integer(), nullable=False), sa.Column("is_cover", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_index(op.f("ix_property_photos_property_id"), "property_photos", ["property_id"], unique=False)
    op.create_table("property_prices", sa.Column("property_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("date", sa.Date(), nullable=False), sa.Column("nightly_price", sa.Numeric(10, 2), nullable=False), sa.Column("minimum_stay", sa.Integer(), nullable=True), sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("property_id", "date", name="uq_property_price_date"))
    op.create_index("ix_property_prices_property_date", "property_prices", ["property_id", "date"], unique=False)
    op.create_table("external_calendar_events", sa.Column("property_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("calendar_source_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("external_uid", sa.String(300), nullable=False), sa.Column("start_date", sa.Date(), nullable=False), sa.Column("end_date", sa.Date(), nullable=False), sa.Column("summary", sa.String(300), nullable=True), sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False), sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.ForeignKeyConstraint(["calendar_source_id"], ["calendar_sources.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["property_id"], ["properties.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("calendar_source_id", "external_uid", name="uq_external_calendar_event_source_uid"))
    op.create_index("ix_external_events_property_dates", "external_calendar_events", ["property_id", "start_date", "end_date"], unique=False)
    op.create_table("payments", sa.Column("booking_id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("provider_id", sa.Integer(), nullable=False), sa.Column("external_payment_id", sa.String(240), nullable=False), sa.Column("amount", sa.Numeric(10, 2), nullable=False), sa.Column("currency", sa.String(3), nullable=False), sa.Column("status", sa.String(80), nullable=False), sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["provider_id"], ["payment_providers.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("provider_id", "external_payment_id", name="uq_payment_provider_external_id"))
    op.create_index("ix_payments_booking", "payments", ["booking_id"], unique=False)


def downgrade() -> None:
    op.drop_table("payments")
    op.drop_table("external_calendar_events")
    op.drop_table("property_prices")
    op.drop_table("property_photos")
    op.drop_table("property_blocks")
    op.drop_table("property_feature_links")
    op.drop_table("calendar_sources")
    op.drop_table("bookings")
    op.drop_table("properties")
    op.drop_table("property_features")
    op.drop_table("admin_users")
    op.drop_table("calendar_providers")
    op.drop_table("payment_providers")
    op.drop_table("payment_statuses")
    op.drop_table("booking_statuses")
    op.drop_table("booking_sources")
