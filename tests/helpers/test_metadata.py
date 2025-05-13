from datetime import datetime
from typing import Any

import pytest

from resnap.helpers.metadata import Metadata, MetadataFail, MetadataSuccess
from resnap.helpers.status import Status
from resnap.helpers.utils import hash_arguments

hashed_arguments: str = hash_arguments({"key": "value"})


class TestMetadata:
    @pytest.mark.parametrize(
        "data, expected",
        [
            (
                {
                    "status": "SUCCESS",
                    "event_time": "2021-01-01T00:00:00",
                    "hashed_arguments": hashed_arguments,
                    "result_path": "/path/to/result",
                    "result_type": "str",
                },
                MetadataSuccess,
            ),
            (
                {
                    "status": "FAIL",
                    "event_time": "2021-01-01T00:00:00",
                    "hashed_arguments": hash_arguments({}),
                    "error_message": "Something went wrong",
                },
                MetadataFail,
            ),
        ],
    )
    def test_should_return_metadata(self, data: dict[str, Any], expected: Metadata) -> None:
        # When
        metadata = Metadata.from_dict(data)

        # Then
        assert isinstance(metadata, expected)


class TestMetadataSuccess:
    def test_should_return_dict(self) -> None:
        # Given
        metadata = MetadataSuccess(
            status=Status.SUCCESS,
            event_time=datetime.fromisoformat("2021-01-01T00:00:00"),
            hashed_arguments=hashed_arguments,
            result_path="/path/to/result",
            result_type="str",
            extra_metadata={"key": "value"},
        )

        # When
        result = metadata.to_dict()

        # Then
        assert result == {
            "status": "SUCCESS",
            "event_time": "2021-01-01T00:00:00",
            "hashed_arguments": hashed_arguments,
            "result_path": "/path/to/result",
            "result_type": "str",
            "extra_metadata": {"key": "value"},
        }

    def test_should_return_metadata_from_dict(self) -> None:
        # Given
        data = {
            "status": "SUCCESS",
            "event_time": "2021-01-01T00:00:00",
            "hashed_arguments": hashed_arguments,
            "result_path": "/path/to/result",
            "result_type": "str",
            "extra_metadata": {"key": "value"},
        }

        # When
        metadata = MetadataSuccess.from_dict(data)

        # Then
        assert metadata.status == Status.SUCCESS
        assert metadata.event_time == datetime.fromisoformat("2021-01-01T00:00:00")
        assert metadata.hashed_arguments == hashed_arguments
        assert metadata.result_path == "/path/to/result"
        assert metadata.result_type == "str"
        assert metadata.extra_metadata == {"key": "value"}


class TestMetadataFail:
    def test_should_return_dict_without_data(self) -> None:
        # Given
        metadata = MetadataFail(
            status=Status.FAIL,
            event_time=datetime.fromisoformat("2021-01-01T00:00:00"),
            hashed_arguments=hashed_arguments,
            error_message="oopsi an error",
            data={},
            extra_metadata={},
        )

        # When
        result = metadata.to_dict()

        # Then
        assert result == {
            "status": "FAIL",
            "event_time": "2021-01-01T00:00:00",
            "hashed_arguments": hashed_arguments,
            "error_message": "oopsi an error",
        }

    def test_should_return_dict_with_data(self) -> None:
        # Given
        metadata = MetadataFail(
            status=Status.FAIL,
            event_time=datetime.fromisoformat("2021-01-01T00:00:00"),
            hashed_arguments=hashed_arguments,
            error_message="oopsi an error",
            data={"key": "value"},
            extra_metadata={"key": "value"},
        )

        # When
        result = metadata.to_dict()

        # Then
        assert result == {
            "status": "FAIL",
            "event_time": "2021-01-01T00:00:00",
            "hashed_arguments": hashed_arguments,
            "error_message": "oopsi an error",
            "data": {"key": "value"},
            "extra_metadata": {"key": "value"},
        }

    def test_should_return_metadata_from_dict(self) -> None:
        # Given
        data = {
            "status": "FAIL",
            "event_time": "2021-01-01T00:00:00",
            "hashed_arguments": hashed_arguments,
            "error_message": "oopsi an error",
            "extra_metadata": {"key": "value"},
        }

        # When
        metadata = MetadataFail.from_dict(data)

        # Then
        assert metadata.status == Status.FAIL
        assert metadata.event_time == datetime.fromisoformat("2021-01-01T00:00:00")
        assert metadata.hashed_arguments == hashed_arguments
        assert metadata.error_message == "oopsi an error"
        assert not metadata.data
        assert metadata.extra_metadata == {"key": "value"}
