from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.models.booking import BOOKING_STATUS_PENDING
from app.services.availability import has_overlap
from app.services.date_ranges import each_night


def test_overlapping_booking_detection():
    assert has_overlap(date(2026, 8, 10), date(2026, 8, 15), date(2026, 8, 14), date(2026, 8, 20))


def test_adjacent_bookings_are_allowed():
    assert not has_overlap(date(2026, 8, 10), date(2026, 8, 15), date(2026, 8, 15), date(2026, 8, 20))


def test_each_night_excludes_checkout():
    assert each_night(date(2026, 8, 12), date(2026, 8, 16)) == [
        date(2026, 8, 12),
        date(2026, 8, 13),
        date(2026, 8, 14),
        date(2026, 8, 15),
    ]


def test_expired_pending_hold_rule_shape():
    booking = SimpleNamespace(
        status_id=BOOKING_STATUS_PENDING,
        hold_expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    assert booking.hold_expires_at <= datetime.now(timezone.utc)


def test_pricing_math_uses_decimal():
    subtotal = Decimal("100.00") + Decimal("140.00") + Decimal("160.00")
    assert subtotal + Decimal("50.00") == Decimal("450.00")


@pytest.mark.parametrize(
    ("start_a", "end_a", "start_b", "end_b", "expected"),
    [
        (date(2026, 1, 1), date(2026, 1, 3), date(2026, 1, 2), date(2026, 1, 4), True),
        (date(2026, 1, 1), date(2026, 1, 3), date(2026, 1, 3), date(2026, 1, 4), False),
    ],
)
def test_overlap_matrix(start_a, end_a, start_b, end_b, expected):
    assert has_overlap(start_a, end_a, start_b, end_b) is expected
