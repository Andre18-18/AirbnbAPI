"""normalize defined value columns

Revision ID: 0002_lookup_values
Revises: 0001_initial
Create Date: 2026-08-10
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0002_lookup_values"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


LOOKUPS = {
    "booking_sources": [(1, "DIRECT"), (2, "AIRBNB"), (3, "BOOKING"), (4, "MANUAL"), (5, "OTHER")],
    "booking_statuses": [(1, "PENDING"), (2, "CONFIRMED"), (3, "CANCELLED"), (4, "EXPIRED")],
    "payment_statuses": [(1, "NOT_REQUIRED"), (2, "PENDING"), (3, "PAID"), (4, "FAILED"), (5, "REFUNDED")],
    "payment_providers": [(1, "STRIPE")],
    "calendar_providers": [(1, "AIRBNB"), (2, "BOOKING"), (3, "VRBO"), (4, "OTHER")],
}


def table_exists(table_name: str) -> bool:
    return table_name in inspect(op.get_bind()).get_table_names()


def column_exists(table_name: str, column_name: str) -> bool:
    if not table_exists(table_name):
        return False
    return column_name in {column["name"] for column in inspect(op.get_bind()).get_columns(table_name)}


def ensure_lookup_table(table_name: str, rows: list[tuple[int, str]]) -> None:
    if not table_exists(table_name):
        op.create_table(
            table_name,
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(40), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("name"),
        )
    for row_id, name in rows:
        op.execute(
            sa.text(f"insert into {table_name} (id, name) values (:id, :name) on conflict (id) do nothing").bindparams(
                id=row_id,
                name=name,
            )
        )


def add_lookup_fk(table_name: str, old_column: str, new_column: str, lookup_table: str) -> None:
    if not table_exists(table_name) or column_exists(table_name, new_column):
        return
    op.add_column(table_name, sa.Column(new_column, sa.Integer(), nullable=True))
    op.execute(
        sa.text(
            f"""
            update {table_name}
            set {new_column} = lookup.id
            from {lookup_table} lookup
            where lookup.name = {table_name}.{old_column}::text
            """
        )
    )
    op.alter_column(table_name, new_column, nullable=False)
    op.create_foreign_key(f"fk_{table_name}_{new_column}", table_name, lookup_table, [new_column], ["id"])
    op.drop_column(table_name, old_column)


def upgrade() -> None:
    for table_name, rows in LOOKUPS.items():
        ensure_lookup_table(table_name, rows)

    if table_exists("bookings"):
        if column_exists("bookings", "status") and not column_exists("bookings", "status_id"):
            op.drop_index("ix_bookings_property_status", table_name="bookings")
        add_lookup_fk("bookings", "source", "source_id", "booking_sources")
        add_lookup_fk("bookings", "status", "status_id", "booking_statuses")
        add_lookup_fk("bookings", "payment_status", "payment_status_id", "payment_statuses")
        if not any(index["name"] == "ix_bookings_property_status" for index in inspect(op.get_bind()).get_indexes("bookings")):
            op.create_index("ix_bookings_property_status", "bookings", ["property_id", "status_id"], unique=False)

    add_lookup_fk("calendar_sources", "provider", "provider_id", "calendar_providers")

    if table_exists("payments") and column_exists("payments", "provider") and not column_exists("payments", "provider_id"):
        op.drop_constraint("uq_payment_provider_external_id", "payments", type_="unique")
    add_lookup_fk("payments", "provider", "provider_id", "payment_providers")
    if table_exists("payments") and not any(
        constraint["name"] == "uq_payment_provider_external_id"
        for constraint in inspect(op.get_bind()).get_unique_constraints("payments")
    ):
        op.create_unique_constraint("uq_payment_provider_external_id", "payments", ["provider_id", "external_payment_id"])

    op.execute("drop type if exists booking_source")
    op.execute("drop type if exists booking_status")
    op.execute("drop type if exists payment_status")
    op.execute("drop type if exists payment_provider")
    op.execute("drop type if exists calendar_provider")


def downgrade() -> None:
    raise NotImplementedError("This development migration is not safely reversible.")
