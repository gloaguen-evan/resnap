from configparser import SectionProxy
from dataclasses import dataclass
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
def test_calculate_datetime_from_now(value: int, unit: TimeUnit, delta: timedelta) -> None:
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


@dataclass
class TestDataClass:
    arg_str: str
    arg_int: int
    arg_list: list[int]
    arg_df: pd.DataFrame | None = None


class TestClass:
    def __init__(self, arg_str: str, arg_int: int, arg_list: list[int], arg_df: pd.DataFrame | None = None) -> None:
        self.arg_str = arg_str
        self.arg_int = arg_int
        self.arg_list = arg_list
        self.arg_df = arg_df


@pytest.mark.parametrize(
    "arguments, expected",
    [
        (
            {"arg_str": "test", "arg_int": 42, "arg_list": [1, 2, 3]},
            "33e639b122556d8ad669ae7dcc9cf6576c0fdb6db6058acf0de5af199822b0be",
        ),
        (
            {"arg_int": 42, "arg_list": [1, 2, 3], "arg_str": "test"},
            "33e639b122556d8ad669ae7dcc9cf6576c0fdb6db6058acf0de5af199822b0be",
        ),
        (
            {"arg_int": 42, "arg_tuple": (1, 2, 3), "arg_str": "test"},
            "ac616acb116c3f94bce02223d7544c49c41cc431798fe3c39e38f9cefc03ac2b",
        ),
        (
            {"arg_int": 42, "arg_set": {1, 2, 3}, "arg_str": "test"},
            "f3868811a5ec3310128f870c3c25b05d8f32999696cfee883ed07b4862aefc63",
        ),
        (
            {"arg_df": pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]}), "arg_str": "test"},
            "309f001ffe0ee049f7fa34f32f7668424e589a73795257a20e652dfaf78b73e8",
        ),
        (
            {"arg_df": pd.DataFrame({"A": [3, 2, 1], "B": [6, 5, 4]}), "arg_str": "test"},
            "cbaa16e213cf07f92cdd588522e8ffc458bc14b8acf89fce7196539ef1116e50",
        ),
        (
            {"args_dataclass": TestDataClass("test", 42, [1, 2, 3], arg_df=pd.DataFrame({"A": [1, 2], "B": [3, 4]}))},
            "cf807ac07815f225022df95c32adec700dc71e7a11331187aa1f0c74f8aa8237",
        ),
        (
            {"args_class": TestClass("test", 42, [1, 2, 3], arg_df=pd.DataFrame({"A": [1, 2], "B": [3, 4]}))},
            "54af02a514923a8f229e1bf8c39fd5d63e7b2d939a76ea0bf585be82284ffe13",
        ),
        (
            {"arg_slice": slice(1, 5, 2), "arg_str": "test"},
            "1bdd21fe2e391a88faf9671df103d38d55bcc6f6e17ef3b6d0e373ba89e8bf5c",
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
