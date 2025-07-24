from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import freezegun
import pytest

from resnap.helpers.constants import META_EXT
from resnap.helpers.time_utils import (
    TimeUnit,
    calculate_datetime_from_now,
    get_datetime_from_filename,
    get_timezone_from_string,
)

FIXED_NOW = datetime(2025, 7, 29, 12, 30, 30)


@pytest.mark.parametrize(
    "value, unit, expected",
    [
        (10, TimeUnit.SECOND, datetime(2025, 7, 29, 12, 30, 30 - 10)),
        (10, TimeUnit.MINUTE, datetime(2025, 7, 29, 12, 30 - 10, 30)),
        (10, TimeUnit.HOUR, datetime(2025, 7, 29, 12 - 10, 30, 30)),
        (10, TimeUnit.DAY, datetime(2025, 7, 29 - 10 + 1, 0, 0, 0)),
        (2, TimeUnit.WEEK, datetime(2025, 7, 29 - 14, 12, 30, 30)),
    ],
)
@freezegun.freeze_time(FIXED_NOW)
def test_calculate_datetime_from_now(value: int, unit: TimeUnit, expected: datetime) -> None:
    # When
    result = calculate_datetime_from_now(value, unit)

    # Then
    assert result == expected


@pytest.mark.parametrize(
    "filename, expected",
    [
        (
            f"toto_2021-01-01T00-00-00{META_EXT}",
            datetime.fromisoformat("2021-01-01T00:00:00"),
        ),
        (
            Path(f"toto_2021-01-01T00-00-00{META_EXT}"),
            datetime.fromisoformat("2021-01-01T00:00:00"),
        ),
        (
            Path(f"toto/toto_2021-01-01T00-00-00{META_EXT}"),
            datetime.fromisoformat("2021-01-01T00:00:00"),
        ),
    ],
)
def test_should_extract_datetime_from_filename(filename: Path | str, expected: datetime) -> None:
    # When
    result = get_datetime_from_filename(filename)

    # Then
    assert result == expected


@pytest.mark.parametrize(
    "input_timezone",
    [
        (None),
        (timezone.utc),
        (ZoneInfo("Europe/Paris")),
    ],
)
def test_should_set_timezone_correctly(input_timezone: timezone | ZoneInfo | None) -> None:
    # Given
    expected = datetime.now(input_timezone)

    # When
    result = calculate_datetime_from_now(0, TimeUnit.SECOND, tz=input_timezone)

    # Then
    assert abs((result - expected).total_seconds()) < 1


@pytest.mark.parametrize(
    "tz, expected",
    [
        ("utc", timezone.utc),
        ("UTC", timezone.utc),
        ("UTC+1", timezone(timedelta(hours=1))),
        ("Europe/Paris", ZoneInfo("Europe/Paris")),
    ],
)
def test_should_return_timezone_from_string(tz: str, expected: timezone | ZoneInfo) -> None:
    # When
    result = get_timezone_from_string(tz)

    # Then
    assert result == expected
