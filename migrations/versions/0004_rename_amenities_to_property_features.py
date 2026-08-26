"""rename amenities tables to property features

Revision ID: 0004_property_features
Revises: 0003_admin_auth_roles
Create Date: 2026-08-11
"""

from alembic import op
from sqlalchemy import inspect

revision = "0004_property_features"
down_revision = "0003_admin_auth_roles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    tables = set(inspect(op.get_bind()).get_table_names())
    if "amenities" in tables and "property_features" not in tables:
        op.rename_table("amenities", "property_features")
    if "property_amenities" in tables and "property_feature_links" not in tables:
        op.rename_table("property_amenities", "property_feature_links")
    columns = {column["name"] for column in inspect(op.get_bind()).get_columns("property_feature_links")}
    if "amenity_id" in columns and "feature_id" not in columns:
        op.alter_column("property_feature_links", "amenity_id", new_column_name="feature_id")
    op.execute("alter index if exists ix_amenities_name rename to ix_property_features_name")


def downgrade() -> None:
    op.execute("alter index if exists ix_property_features_name rename to ix_amenities_name")
    op.alter_column("property_feature_links", "feature_id", new_column_name="amenity_id")
    op.rename_table("property_feature_links", "property_amenities")
    op.rename_table("property_features", "amenities")
