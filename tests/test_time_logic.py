from datetime import datetime, timezone

import pytest

from app.time_logic import (
    InvalidTimeFormatError,
    InvalidTimezoneError,
    compute_state,
)


def _utc(year, month, day, hour, minute):
    return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)


def test_inside_working_hours():
    state = compute_state(
        "America/New_York", "09:00", "17:00", now=_utc(2026, 6, 15, 18, 0)
    )
    assert state.is_working is True
    assert state.time_str == "2:00 pm"
    assert state.tz_label.startswith("America/New_York ")


def test_outside_working_hours():
    state = compute_state(
        "America/New_York", "09:00", "17:00", now=_utc(2026, 6, 15, 23, 0)
    )
    assert state.is_working is False
    assert state.time_str == "7:00 pm"


def test_overnight_shift_is_working():
    state = compute_state(
        "America/New_York", "22:00", "06:00", now=_utc(2026, 6, 15, 6, 0)
    )
    assert state.time_str == "2:00 am"
    assert state.is_working is True


def test_overnight_shift_off_hours():
    state = compute_state(
        "America/New_York", "22:00", "06:00", now=_utc(2026, 6, 15, 16, 0)
    )
    assert state.time_str == "12:00 pm"
    assert state.is_working is False


def test_dst_spring_forward_no_crash():
    state = compute_state(
        "America/New_York", "09:00", "17:00", now=_utc(2026, 3, 8, 7, 30)
    )
    assert state.time_str == "3:30 am"
    assert state.is_working is False


def test_unknown_timezone_raises():
    with pytest.raises(InvalidTimezoneError):
        compute_state("Foo/Bar", "09:00", "17:00", now=_utc(2026, 6, 15, 12, 0))


def test_invalid_time_format_raises():
    with pytest.raises(InvalidTimeFormatError):
        compute_state("UTC", "9am", "17:00", now=_utc(2026, 6, 15, 12, 0))
