from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

_HHMM_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


class InvalidTimezoneError(ValueError):
    pass


class InvalidTimeFormatError(ValueError):
    pass


@dataclass(frozen=True)
class TimeState:
    time_str: str
    date_str: str
    tz_label: str
    is_working: bool


def _parse_hhmm(value: str, field: str) -> time:
    match = _HHMM_RE.match(value)
    if not match:
        raise InvalidTimeFormatError(f"Invalid time format for {field}: {value!r}")
    return time(int(match.group(1)), int(match.group(2)))


def _is_within_window(now_t: time, start_t: time, end_t: time) -> bool:
    if start_t == end_t:
        return False
    if start_t < end_t:
        return start_t <= now_t < end_t
    return now_t >= start_t or now_t < end_t


def compute_state(
    tz: str,
    start: str,
    end: str,
    now: datetime | None = None,
) -> TimeState:
    try:
        zone = ZoneInfo(tz)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise InvalidTimezoneError(f"Unknown timezone: {tz!r}") from exc

    start_t = _parse_hhmm(start, "start")
    end_t = _parse_hhmm(end, "end")

    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    local_now = now.astimezone(zone)
    abbrev = local_now.tzname() or ""
    tz_label = f"{tz} {abbrev}".strip()

    return TimeState(
        time_str=local_now.strftime("%H:%M"),
        date_str=local_now.strftime("%A, %B %-d %Y"),
        tz_label=tz_label,
        is_working=_is_within_window(local_now.time(), start_t, end_t),
    )
