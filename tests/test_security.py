from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from jose import jwt
from pydantic import ValidationError

from app.core.config import get_settings
from app.core.dependencies import ROLE_RANK
from app.core.security import create_access_token, decode_access_token, hash_password, normalize_email, verify_password
from app.models.admin_user import USER_PROPERTY_ROLE_MANAGER, USER_PROPERTY_ROLE_OWNER, USER_PROPERTY_ROLE_STAFF
from app.schemas.booking import BookingAdminUpdate
from app.schemas.property import PriceOverrideUpsert, PropertyBlockCreate
from app.services.calendar_sync import validate_public_ical_url


def test_password_hash_uses_argon2id():
    password_hash = hash_password("correct horse battery staple")
    assert password_hash.startswith("$argon2id$")
    assert verify_password("correct horse battery staple", password_hash)
    assert not verify_password("wrong password", password_hash)


def test_email_normalization():
    assert normalize_email(" Admin@Example.COM ") == "admin@example.com"


def test_access_token_contains_subject_and_session():
    user_id = uuid4()
    session_id = uuid4()
    token = create_access_token(user_id, session_id)
    assert decode_access_token(token) == (user_id, session_id)


def test_expired_access_token_is_rejected():
    settings = get_settings()
    token = jwt.encode(
        {"sub": str(uuid4()), "sid": str(uuid4()), "typ": "access", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    with pytest.raises(Exception):
        decode_access_token(token)


def test_invalid_token_is_rejected():
    with pytest.raises(Exception):
        decode_access_token("not-a-token")


def test_role_ordering():
    assert ROLE_RANK[USER_PROPERTY_ROLE_OWNER] > ROLE_RANK[USER_PROPERTY_ROLE_MANAGER] > ROLE_RANK[USER_PROPERTY_ROLE_STAFF]


def test_admin_booking_update_rejects_mass_assignment():
    with pytest.raises(ValidationError):
        BookingAdminUpdate.model_validate(
            {
                "property_id": str(uuid4()),
                "guest_name": "Guest Name",
                "guest_email": "guest@example.com",
                "check_in": "2027-01-10",
                "check_out": "2027-01-12",
                "number_of_guests": 2,
            }
        )


def test_invalid_date_ranges_are_rejected():
    with pytest.raises(ValidationError):
        PropertyBlockCreate.model_validate({"property_id": str(uuid4()), "start_date": "2027-01-10", "end_date": "2027-01-10"})
    with pytest.raises(ValidationError):
        PriceOverrideUpsert.model_validate({"property_id": str(uuid4()), "start_date": "2027-01-10", "end_date": "2027-01-09"})


@pytest.mark.parametrize("url", ["http://localhost/calendar.ics", "http://127.0.0.1/calendar.ics", "ftp://example.com/calendar.ics"])
def test_ical_url_rejects_unsafe_destinations(url):
    with pytest.raises(ValueError):
        validate_public_ical_url(url)
