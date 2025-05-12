from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import pytest

from resnap.helpers.utils import TimeUnit, calculate_datetime_from_now, get_datetime_from_filename, hash_arguments


@pytest.mark.parametrize(
    "value, unit, expected",
    [
        (10, TimeUnit.SECOND, datetime.now() - timedelta(seconds=10)),
        (10, TimeUnit.MINUTE, datetime.now() - timedelta(minutes=10)),
        (10, TimeUnit.HOUR, datetime.now() - timedelta(hours=10)),
        (10, TimeUnit.DAY, datetime.now() - timedelta(days=10)),
        (10, TimeUnit.WEEK, datetime.now() - timedelta(weeks=10)),
    ],
)
def test_calculate_datetime_from_now(value: int, unit: TimeUnit, expected: datetime) -> None:
    # When
    result = calculate_datetime_from_now(value, unit)

    # Then
    assert abs((result - expected).total_seconds()) < 1


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("toto_2021-01-01T00:00:00.resnap", datetime.fromisoformat("2021-01-01T00:00:00")),
        (Path("toto_2021-01-01T00:00:00.resnap"), datetime.fromisoformat("2021-01-01T00:00:00")),
        (Path("toto/toto_2021-01-01T00:00:00.resnap"), datetime.fromisoformat("2021-01-01T00:00:00")),
    ],
)
def test_should_extract_datetime_from_filename(filename: Path | str, expected: datetime) -> None:
    # When
    result = get_datetime_from_filename(filename)

    # Then
    assert result == expected


@pytest.mark.parametrize(
    "arguments, expected",
    [
        (
            {"arg_str": "test", "arg_int": 42, "arg_list": [1, 2, 3]},
            "bc142dc6f6399ecf5b5637b0e82fd6efc997bb41ac2a6822c9807def85d6f5f1"
        ),
        (
            {"arg_int": 42, "arg_list": [1, 2, 3], "arg_str": "test"},
            "2fa503a4eecf5750e99829c24fa020b28bfc01353e518f3d7d86835f2eaf291b"
        ),
        (
            {"arg_df": pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]}), "arg_str": "test"},
            "cd65480c72245387cccae12f49f68b145cfb6501c8fcffbdef9afdfe7792102a"
        ),
        (
            {"arg_df": pd.DataFrame({"A": [3, 2, 1], "B": [6, 5, 4]}), "arg_str": "test"},
            "d6b60d43b5c485e6cac69016bdd0eaf0a3436fdba27f9c45e2eae19491e2e202"
        ),
    ],
)
def test_should_hash_arguments(arguments: dict[str, Any], expected: str) -> None:
    # When
    result = hash_arguments(arguments)

    # Then
    assert result == expected
