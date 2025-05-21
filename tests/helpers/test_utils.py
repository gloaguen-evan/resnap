from configparser import SectionProxy
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import pytest

from resnap.helpers.utils import (
    TimeUnit,
    calculate_datetime_from_now,
    get_datetime_from_filename,
    hash_arguments,
    load_file,
)


@pytest.mark.parametrize(
    "value, unit, delta",
    [
        (10, TimeUnit.SECOND, timedelta(seconds=10)),
        (10, TimeUnit.MINUTE, timedelta(minutes=10)),
        (10, TimeUnit.HOUR, timedelta(hours=10)),
        (10, TimeUnit.DAY, timedelta(days=10)),
        (10, TimeUnit.WEEK, timedelta(weeks=10)),
    ],
)
def test_calculate_datetime_from_now(value: int, unit: TimeUnit, delta: datetime) -> None:
    # Given
    now = datetime.now()

    # When
    result = calculate_datetime_from_now(value, unit)

    # Then
    expected = now - delta
    assert abs((result - expected).total_seconds()) < 1


@pytest.mark.parametrize(
    "filename, expected",
    [
        (
            "toto_2021-01-01T00-00-00.resnap",
            datetime.fromisoformat("2021-01-01T00:00:00"),
        ),
        (
            Path("toto_2021-01-01T00-00-00.resnap"),
            datetime.fromisoformat("2021-01-01T00:00:00"),
        ),
        (
            Path("toto/toto_2021-01-01T00-00-00.resnap"),
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
    "arguments, expected",
    [
        (
            {"arg_str": "test", "arg_int": 42, "arg_list": [1, 2, 3]},
            "bc142dc6f6399ecf5b5637b0e82fd6efc997bb41ac2a6822c9807def85d6f5f1",
        ),
        (
            {"arg_int": 42, "arg_list": [1, 2, 3], "arg_str": "test"},
            "2fa503a4eecf5750e99829c24fa020b28bfc01353e518f3d7d86835f2eaf291b",
        ),
        (
            {
                "arg_df": pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]}),
                "arg_str": "test",
            },
            "cd65480c72245387cccae12f49f68b145cfb6501c8fcffbdef9afdfe7792102a",
        ),
        (
            {
                "arg_df": pd.DataFrame({"A": [3, 2, 1], "B": [6, 5, 4]}),
                "arg_str": "test",
            },
            "d6b60d43b5c485e6cac69016bdd0eaf0a3436fdba27f9c45e2eae19491e2e202",
        ),
    ],
)
def test_should_hash_arguments(arguments: dict[str, Any], expected: str) -> None:
    # When
    result = hash_arguments(arguments)

    # Then
    assert result == expected


@pytest.mark.parametrize(
    "file_path, result_type",
    [
        ("test-secrets.json", dict),
        ("test-secrets.yml", dict),
        ("test-secrets.cfg", SectionProxy),
    ],
)
def test_should_load_yaml_file(file_path: str, result_type: dict | SectionProxy) -> None:
    # Given
    file_path = Path(__file__).parent.parent / "data" / "config" / file_path

    # When
    result = load_file(str(file_path), key="s3")

    # Then
    assert isinstance(result, result_type)
    assert result["server"] == "server"
    assert result["access_key"] == "access_key"
    assert result["secret_key"] == "secret_key"
    assert result["bucket"] == "bucket"


def test_should_raise_value_error_when_file_format_is_not_supported() -> None:
    # Given
    file_path = Path(__file__).parent.parent / "data" / "config" / "test-secrets.txt"

    # When / Then
    with pytest.raises(ValueError, match="File format not supported"):
        load_file(str(file_path))


def test_should_raise_key_error_when_key_is_not_found() -> None:
    # Given
    file_path = Path(__file__).parent.parent / "data" / "config" / "test-secrets.cfg"

    # When
    with pytest.raises(KeyError) as e:
        load_file(str(file_path), key="non_existent")

    # Then
    assert "Key non_existent not found" in str(e.value)
