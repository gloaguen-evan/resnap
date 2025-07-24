from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Protocol
from zoneinfo import ZoneInfo

from .constants import EXT


class TimeUnit(str, Enum):
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"


# Date calculator interface


class DateTimeCalculator(Protocol):
    def __call__(self, now: datetime, value: int) -> datetime: ...


# Implementations


def _seconds_calculator(now: datetime, value: int) -> datetime:
    return now - timedelta(seconds=value)


def _minutes_calculator(now: datetime, value: int) -> datetime:
    return now - timedelta(minutes=value)


def _hours_calculator(now: datetime, value: int) -> datetime:
    return now - timedelta(hours=value)


def _days_calculator(now: datetime, value: int) -> datetime:
    start_of_day_n_days_ago = (now - timedelta(days=value - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return start_of_day_n_days_ago


def _week_calculator(now: datetime, value: int) -> datetime:
    return now - timedelta(weeks=value)


# Strategy dict


_TIME_UNIT_TO_CALCULATOR: dict[TimeUnit, DateTimeCalculator] = {
    TimeUnit.SECOND: _seconds_calculator,
    TimeUnit.MINUTE: _minutes_calculator,
    TimeUnit.HOUR: _hours_calculator,
    TimeUnit.DAY: _days_calculator,
    TimeUnit.WEEK: _week_calculator,
}


# Public API


def calculate_datetime_from_now(value: int, unit: TimeUnit, tz: timezone | None = None) -> datetime:
    """
    Calculate datetime from now based on the given value and unit.

    Args:
        value (int): The value to calculate the datetime from now.
        unit (TimeUnit): The unit to calculate the datetime from now.
        tz (timezone): The timezone to use for the calculation.
    Returns:
        datetime: The calculated datetime from now.
    """
    now = datetime.now(tz)
    return _TIME_UNIT_TO_CALCULATOR[unit](now, value)


def get_timezone_from_string(tz_str: str) -> timezone | ZoneInfo:
    """
    Get timezone from the given string.

    Args:
        tz_str (str): The timezone string to convert.
    Returns:
        timezone | ZoneInfo: The timezone object corresponding to the given string.
    """
    if "utc" in tz_str.lower():
        tz_str_without_utc = tz_str.lower().replace("utc", "").strip()
        if not tz_str_without_utc:
            return timezone.utc
        return timezone(timedelta(hours=int(tz_str_without_utc)))

    return ZoneInfo(tz_str)


def get_datetime_from_filename(filename: Path | str) -> datetime:
    """
    Get datetime from the given filename.

    Args:
        filename (Path | str): The filename to get the datetime from.
    Returns:
        datetime: The datetime from the given filename.
    """
    filename_without_ext: str = str(filename).split(EXT)[0]
    extract_day, extract_time = filename_without_ext.split("_")[-1].split("T")
    extract_time = extract_time.replace("-", ":")
    return datetime.fromisoformat(f"{extract_day}T{extract_time}")
