from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, call

import freezegun
import pandas as pd
import pytest

from resnap.helpers.metadata import MetadataFail, MetadataSuccess
from resnap.helpers.singleton import SingletonABCMeta
from resnap.helpers.status import Status
from resnap.helpers.utils import hash_arguments
from resnap.services.local_service import LocalResnapService
from tests.builders.config_builder import ConfigBuilder


@pytest.fixture(autouse=True)
def reset_singletons() -> None:
    SingletonABCMeta._instances = {}


@pytest.fixture(autouse=True)
def mock_read_parquet_to_dataframe(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch(
        "resnap.services.local_service.LocalResnapService._read_parquet_to_dataframe"
    )
    return mock


@pytest.fixture(autouse=True)
def mock_read_csv_to_dataframe(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch(
        "resnap.services.local_service.LocalResnapService._read_csv_to_dataframe"
    )
    return mock


@pytest.fixture(autouse=True)
def mock_read_pickle(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch(
        "resnap.services.local_service.LocalResnapService._read_pickle"
    )
    return mock


@pytest.fixture(autouse=True)
def mock_read_text(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch(
        "resnap.services.local_service.LocalResnapService._read_text"
    )
    return mock


@pytest.fixture(autouse=True)
def mock_read_json(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch(
        "resnap.services.local_service.LocalResnapService._read_json"
    )
    return mock


@pytest.fixture(autouse=True)
def mock_save_dataframe_to_parquet(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch(
        "resnap.services.local_service.LocalResnapService._save_dataframe_to_parquet"
    )
    return mock


@pytest.fixture(autouse=True)
def mock_save_dataframe_to_csv(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch(
        "resnap.services.local_service.LocalResnapService._save_dataframe_to_csv"
    )
    return mock


@pytest.fixture(autouse=True)
def mock_save_to_pickle(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch(
        "resnap.services.local_service.LocalResnapService._save_to_pickle"
    )
    return mock


@pytest.fixture(autouse=True)
def mock_save_to_text(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch(
        "resnap.services.local_service.LocalResnapService._save_to_text"
    )
    return mock


@pytest.fixture(autouse=True)
def mock_save_to_json(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch(
        "resnap.services.local_service.LocalResnapService._save_to_json"
    )
    return mock


@pytest.fixture(autouse=True)
def mock_write_metadata(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch(
        "resnap.services.local_service.LocalResnapService._write_metadata"
    )
    return mock


@pytest.fixture(autouse=True)
def mock_create_folder(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch(
        "resnap.services.local_service.LocalResnapService._create_folder"
    )
    return mock


class TestServicce:
    hashed_arguments: str = hash_arguments({"toto": "toto"})

    @pytest.mark.parametrize("enabled", [True, False])
    def test_should_return_if_service_is_enabled(self, enabled: bool) -> None:
        # Given
        service = LocalResnapService(
            config=ConfigBuilder.a_config().is_enabled(enabled).build()
        )
        assert service.is_enabled == enabled

    @pytest.mark.parametrize(
        "output_path, output_folder, expected",
        [
            ("", "", "test_2021-01-01T00-00-00.resnap"),
            ("output", "", "output/test_2021-01-01T00-00-00.resnap"),
            ("output", "test", "output/test/test_2021-01-01T00-00-00.resnap"),
        ],
    )
    def test_should_return_metadata_path(
        self, output_path: str, output_folder: str, expected: str
    ) -> None:
        # Given
        service = LocalResnapService(
            config=ConfigBuilder.a_config().with_output_base_path(output_path).build()
        )
        func_name = "test"
        event_time = datetime.fromisoformat("2021-01-01T00:00:00")

        # When
        result = service.metadata_path(func_name, event_time, output_folder)

        # Then
        assert result == expected

    @pytest.mark.parametrize(
        "output_path, output_folder, expected",
        [
            ("", "", "test_2021-01-01T00-00-00.resnap.ext"),
            ("output", "", "output/test_2021-01-01T00-00-00.resnap.ext"),
            ("output", "test", "output/test/test_2021-01-01T00-00-00.resnap.ext"),
        ],
    )
    def test_should_return_result_path(
        self, output_path: str, output_folder: str, expected: str
    ) -> None:
        # Given
        service = LocalResnapService(
            config=ConfigBuilder.a_config().with_output_base_path(output_path).build()
        )
        func_name = "test"
        event_time = datetime.fromisoformat("2021-01-01T00:00:00")

        # When
        result = service.result_path(func_name, event_time, output_folder, "ext")

        # Then
        assert result == expected

    @pytest.mark.parametrize(
        "result_path, expected_mock, result_type",
        [
            ("test_2021-01-01T00-00-00.resnap.pkl", "mock_read_pickle", "str"),
            (
                "test_2021-01-01T00-00-00.resnap.parquet.gz",
                "mock_read_parquet_to_dataframe",
                "pd.DataFrame",
            ),
            (
                "test_2021-01-01T00-00-00.resnap.csv",
                "mock_read_csv_to_dataframe",
                "pd.DataFrame",
            ),
            ("test_2021-01-01T00-00-00.resnap.txt", "mock_read_text", "str"),
            ("test_2021-01-01T00-00-00.resnap.json", "mock_read_json", "str"),
        ],
    )
    def test_should_read_result(
        self,
        result_path: str,
        expected_mock: str,
        result_type: str,
        request: type[pytest.FixtureRequest],
    ) -> None:
        # Given
        mock: MagicMock = request.getfixturevalue(expected_mock)
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        metadata = MetadataSuccess(
            status=Status.SUCCESS,
            event_time=datetime.fromisoformat("2021-01-01T00:00:00"),
            hashed_arguments=hash_arguments({}),
            result_path=result_path,
            result_type=result_type,
        )

        # When
        service.read_result(metadata)

        # Then
        mock.assert_called_once_with(metadata.result_path)

    @pytest.mark.parametrize(
        "result_type, result",
        [
            ("str", "test"),
            ("int", 10),
            ("float", 5.2),
            ("bool", True),
        ],
    )
    def test_should_cast_result_if_file_is_text(
        self, result_type: str, result: Any, mock_read_text: MagicMock
    ) -> None:
        # Given
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        metadata = MetadataSuccess(
            status=Status.SUCCESS,
            event_time=datetime.fromisoformat("2021-01-01T00:00:00"),
            hashed_arguments=hash_arguments({}),
            result_path="test_2021-01-01T00-00-00.resnap.txt",
            result_type=result_type,
        )
        mock_read_text.return_value = str(result)

        # When
        res = service.read_result(metadata)

        # Then
        assert res == result

    @pytest.mark.parametrize(
        "result_path, result_type",
        [
            ("test_2021-01-01T00-00-00.resnap.toto", "str"),
            ("test_2021-01-01T00-00-00.resnap.toto", "pd.DataFrame"),
        ],
    )
    def test_should_raise_not_implemented_error_when_reading_unknown_result_type(
        self,
        result_path: str,
        result_type: str,
    ) -> None:
        # Given
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        metadata = MetadataSuccess(
            status=Status.SUCCESS,
            event_time=datetime.fromisoformat("2021-01-01T00:00:00"),
            hashed_arguments=hash_arguments({}),
            result_path=result_path,
            result_type=result_type,
        )

        # When / Then
        with pytest.raises(
            NotImplementedError, match=f"Unsupported result type: {result_type}"
        ):
            service.read_result(metadata)

    @freezegun.freeze_time("2021-01-01")
    @pytest.mark.parametrize(
        "func_result, output_format, output_folder, expected_mock, expected_result_ext",
        [
            ("toto", None, "", "mock_save_to_pickle", "pkl"),
            ("toto", "pkl", "", "mock_save_to_pickle", "pkl"),
            (10, "txt", "", "mock_save_to_text", "txt"),
            (False, None, "", "mock_save_to_pickle", "pkl"),
            ({"test": 1}, "json", "", "mock_save_to_json", "json"),
            ({"test": 1}, "json", "toto", "mock_save_to_json", "json"),
            (
                pd.DataFrame(
                    {
                        "A": [1, 2, 3],
                        "B": [4, 5, 6],
                        "C": [7, 8, 9],
                    }
                ),
                None,
                "",
                "mock_save_dataframe_to_parquet",
                "parquet.gz",
            ),
            (
                pd.DataFrame(
                    {
                        "A": [1, 2, 3],
                        "B": [4, 5, 6],
                        "C": [7, 8, 9],
                    }
                ),
                "csv",
                "",
                "mock_save_dataframe_to_csv",
                "csv",
            ),
        ],
    )
    def test_should_save_result(
        self,
        func_result: Any,
        output_format: str | None,
        output_folder: str,
        expected_mock: str,
        expected_result_ext: str,
        request: type[pytest.FixtureRequest],
    ) -> None:
        # Given
        mock: MagicMock = request.getfixturevalue(expected_mock)
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        expected_event_time: datetime = datetime.fromisoformat("2021-01-01T00:00:00")
        output_path = f"{output_folder}/" if output_folder else ""
        expected_result_path: str = (
            f"{output_path}test_2021-01-01T00-00-00.resnap.{expected_result_ext}"
        )

        # When
        result_path, event_time = service.save_result(
            "test", func_result, output_folder, output_format
        )

        # Then
        mock.assert_called_once_with(
            result=func_result, result_path=expected_result_path
        )
        assert result_path == expected_result_path
        assert event_time == expected_event_time

    def test_should_save_success_metadata(self, mock_write_metadata: MagicMock) -> None:
        # Given
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        expected_event_time: datetime = datetime.fromisoformat("2021-01-01T00:00:00")
        expected_result_path: str = "test_2021-01-01T00-00-00.resnap.pkl"
        metadata = MetadataSuccess(
            status=Status.SUCCESS,
            event_time=expected_event_time,
            hashed_arguments=self.hashed_arguments,
            result_path=expected_result_path,
            result_type="str",
            extra_metadata={},
        )

        # When
        service.save_success_metadata(
            "test",
            "",
            self.hashed_arguments,
            expected_event_time,
            expected_result_path,
            "str",
            extra_metadata={},
        )

        # Then
        mock_write_metadata.assert_called_once_with(
            "test_2021-01-01T00-00-00.resnap", metadata
        )

    def test_should_save_failed_metadata(self, mock_write_metadata: MagicMock) -> None:
        # Given
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        expected_event_time: datetime = datetime.fromisoformat("2021-01-01T00:00:00")
        metadata = MetadataFail(
            status=Status.FAIL,
            event_time=expected_event_time,
            hashed_arguments=self.hashed_arguments,
            error_message="error",
            data={"id": 1},
            extra_metadata={},
        )

        # When
        service.save_failed_metadata(
            "test",
            "",
            self.hashed_arguments,
            expected_event_time,
            error_message="error",
            data={"id": 1},
            extra_metadata={},
        )

        # Then
        mock_write_metadata.assert_called_once_with(
            "test_2021-01-01T00-00-00.resnap",
            metadata,
        )

    @pytest.mark.parametrize(
        "path, output_folder",
        [
            ("", ""),
            ("results", ""),
            ("results", "test"),
        ],
    )
    def test_should_create_folder(
        self, path: str, output_folder: str, mock_create_folder: MagicMock
    ) -> None:
        # Given
        service = LocalResnapService(
            config=ConfigBuilder.a_config().with_output_base_path(path).build()
        )
        expected_calls = []
        if path:
            expected_calls.append(call("", path))
        if output_folder:
            expected_calls.append(call(path, output_folder))

        # When
        service.create_output_folder(output_folder)

        # Then
        mock_create_folder.assert_has_calls(calls=expected_calls, any_order=True)
