from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from resnap.helpers.metadata import Metadata, MetadataSuccess
from resnap.helpers.status import Status
from resnap.helpers.utils import hash_arguments
from resnap.services.local_service import LocalResnapService
from tests.builders.config_builder import ConfigBuilder


@pytest.fixture
def mock_path_rglob(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch("pathlib.Path.rglob")
    return mock


@pytest.fixture
def mock_path_mkdir(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch("pathlib.Path.mkdir")
    return mock


def get_mock_path_file(name: str, is_file: bool) -> MagicMock:
    mock: MagicMock = MagicMock(
        spec=Path,
        is_dir=MagicMock(return_value=not is_file),
        is_file=MagicMock(return_value=is_file),
        unlink=MagicMock(),
    )
    mock.name = name
    if is_file:
        mock.suffix = f".{name.split('.')[-1]}"
    return mock


class TestLocalService:
    hashed_arguments: str = hash_arguments({"test": "toto"})

    @pytest.mark.parametrize(
        "file_path, is_file, is_deleted",
        [
            ("toto", False, False),
            ("test_2021-01-01T00-00-00.resnap", True, True),
            ("test_2021-01-01T00-00-00.resnap.pkl", True, True),
            ("toto/toto_2021-01-01T00-00-00.csv", True, False),
            (f"test_{datetime.now().isoformat().replace(':', '-')}.resnap", True, False),
        ],
    )
    def test_should_clear_old_saves(
        self,
        file_path: str,
        is_file: bool,
        is_deleted: bool,
        mock_path_rglob: MagicMock,
    ) -> None:
        # Given
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        mock_file = get_mock_path_file(file_path, is_file)
        mock_path_rglob.return_value = [mock_file]

        # When
        service.clear_old_saves()

        # Then
        mock_path_rglob.assert_called_once()
        assert mock_file.unlink.call_count == int(is_deleted)

    def test_clear_old_saves_should_delete_empty_folder(
        self, mock_path_rglob: MagicMock
    ) -> None:
        # Given
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        mock_file = get_mock_path_file("toto", False)
        mock_file.iterdir.return_value = []
        mock_path_rglob.return_value = [mock_file]

        # When
        service.clear_old_saves()

        # Then
        assert mock_file.unlink.call_count == 0
        mock_file.rmdir.assert_called_once()

    def test_clear_old_saves_should_not_delete_unempty_folder(
        self, mock_path_rglob: MagicMock
    ) -> None:
        # Given
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        mock_file = get_mock_path_file("toto", False)
        mock_file.iterdir.return_value = ["test.csv"]
        mock_path_rglob.return_value = [mock_file]

        # When
        service.clear_old_saves()

        # Then
        assert mock_file.unlink.call_count == 0
        mock_file.rmdir.assert_not_called()

    def test_should_read_metadata(self) -> None:
        # Given
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        expected_metadata = MetadataSuccess(
            status=Status.SUCCESS,
            event_time=datetime.fromisoformat("2021-01-01T00:00:00"),
            result_path="test_2021-01-01T00-00-00.resnap.pkl",
            result_type="str",
            hashed_arguments=self.hashed_arguments,
            extra_metadata={},
        )

        # When
        result = service._read_metadata(
            "tests/data/metadata/test-metadata_2021-01-01T00-00-00.resnap"
        )

        # Then
        assert isinstance(result, Metadata)
        assert result == expected_metadata

    def test_should_return_metadatas(self, mock_path_rglob: MagicMock) -> None:
        # Given
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        mock_path_rglob.return_value = [
            Path("tests/data/metadata/test-metadata_2021-01-01T00-00-00.resnap"),
            Path("tests/data/metadata/test-metadata_2024-01-01T00-00-00.resnap"),
            get_mock_path_file("toto", False),
            get_mock_path_file("toto_2021-01-02T00-00-00.resnap", True),
            get_mock_path_file("test.csv", True),
        ]

        # When
        result = service.get_success_metadatas("test", "")

        # Then
        assert result == [
            MetadataSuccess(
                status=Status.SUCCESS,
                event_time=datetime.fromisoformat("2024-01-01T00:00:00"),
                result_path="test_2024-01-01T00-00-00.resnap.pkl",
                result_type="str",
                hashed_arguments=hash_arguments({}),
                extra_metadata={},
            ),
            MetadataSuccess(
                status=Status.SUCCESS,
                event_time=datetime.fromisoformat("2021-01-01T00:00:00"),
                result_path="test_2021-01-01T00-00-00.resnap.pkl",
                result_type="str",
                hashed_arguments=self.hashed_arguments,
                extra_metadata={},
            ),
        ]

    def test_should_return_none_if_not_metadata(
        self, mock_path_rglob: MagicMock
    ) -> None:
        # Given
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        mock_path_rglob.return_value = []

        # When
        result = service.get_success_metadatas("test", "toto")

        # Then
        assert len(result) == 0

    @patch("json.dump")
    @patch("builtins.open")
    def test_should_write_metadata(
        self, mock_open: MagicMock, mock_json_dump: MagicMock
    ) -> None:
        # Given
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        metadata = MetadataSuccess(
            status=Status.SUCCESS,
            event_time=datetime.fromisoformat("2021-01-01T00:00:00"),
            result_path="test_2021-01-01T00-00-00.resnap.pkl",
            result_type="str",
            hashed_arguments=self.hashed_arguments,
        )

        # When
        service._write_metadata("test_2021-01-01T00-00-00.resnap", metadata)

        # Then
        mock_open.assert_called_once()
        mock_json_dump.assert_called_once_with(
            metadata.to_dict(), mock_open.return_value.__enter__(), indent=4
        )

    @patch("pandas.DataFrame.to_parquet")
    def test_should_save_dataframe_to_parquet(self, mock_to_parquet: MagicMock) -> None:
        # Given
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        result = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        result_path = "test.parquet"

        # When
        service._save_dataframe_to_parquet(result, result_path)

        # Then
        mock_to_parquet.assert_called_once_with(result_path, compression="gzip")

    @patch("pickle.dump")
    @patch("builtins.open")
    def test_should_save_to_pickle(
        self, mock_open: MagicMock, mock_pickle_dump: MagicMock
    ) -> None:
        # Given
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        result = {"key": "value"}
        result_path = "test.pkl"

        # When
        service._save_to_pickle(result, result_path)

        # Then
        mock_open.assert_called_once_with(result_path, "wb")
        mock_pickle_dump.assert_called_once_with(
            result, mock_open.return_value.__enter__()
        )

    @patch("pandas.read_parquet")
    def test_should_read_parquet_to_dataframe(
        self, mock_read_parquet: MagicMock
    ) -> None:
        # Given
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        file_path = "test.parquet"
        expected_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_read_parquet.return_value = expected_df

        # When
        result = service._read_parquet_to_dataframe(file_path)

        # Then
        mock_read_parquet.assert_called_once_with(file_path)
        pd.testing.assert_frame_equal(result, expected_df)

    @patch("pickle.load")
    @patch("builtins.open")
    def test_should_read_pickle(
        self, mock_open: MagicMock, mock_pickle_load: MagicMock
    ) -> None:
        # Given
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        file_path = "test.pkl"
        expected_data = {"key": "value"}
        mock_pickle_load.return_value = expected_data

        # When
        result = service._read_pickle(file_path)

        # Then
        mock_open.assert_called_once_with(file_path, "rb")
        mock_pickle_load.assert_called_once_with(mock_open.return_value.__enter__())
        assert result == expected_data

    @patch("json.load")
    @patch("builtins.open")
    def test_should_read_json(
        self, mock_open: MagicMock, mock_json_load: MagicMock
    ) -> None:
        # Given
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        file_path = "test.json"
        expected_data = {"key": "value"}
        mock_json_load.return_value = expected_data

        # When
        result = service._read_json(file_path)

        # Then
        mock_open.assert_called_once_with(file_path, "r")
        mock_json_load.assert_called_once_with(mock_open.return_value.__enter__())
        assert result == expected_data

    @patch("builtins.open")
    def test_should_read_text(self, mock_open: MagicMock) -> None:
        # Given
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        file_path = "test.txt"
        expected_data = "test"
        mock_open.return_value.__enter__().read.return_value = expected_data

        # When
        result = service._read_text(file_path)

        # Then
        mock_open.assert_called_once_with(file_path, "r")
        assert result == expected_data

    @patch("pandas.DataFrame.to_csv")
    def test_should_save_dataframe_to_csv(self, mock_to_csv: MagicMock) -> None:
        # Given
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        result = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        result_path = "test.parquet"

        # When
        service._save_dataframe_to_csv(result, result_path)

        # Then
        mock_to_csv.assert_called_once_with(result_path, index=False)

    @patch("pandas.read_csv")
    def test_should_read_csv_to_dataframe(self, mock_read_csv: MagicMock) -> None:
        # Given
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        file_path = "test.csv"
        expected_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_read_csv.return_value = expected_df

        # When
        result = service._read_csv_to_dataframe(file_path)

        # Then
        mock_read_csv.assert_called_once_with(file_path, index_col=False)
        pd.testing.assert_frame_equal(result, expected_df)

    @patch("builtins.open")
    def test_should_save_to_text(self, mock_open: MagicMock) -> None:
        # Given
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        result = "toto"
        result_path = "test.text"

        # When
        service._save_to_text(result, result_path)

        # Then
        mock_open.assert_called_once_with(result_path, "w")
        mock_open.return_value.__enter__().write.assert_called_once_with(result)

    @patch("json.dump")
    @patch("builtins.open")
    def test_should_save_to_json(
        self, mock_open: MagicMock, mock_json_dump: MagicMock
    ) -> None:
        # Given
        service = LocalResnapService(config=ConfigBuilder.a_config().build())
        result = {"key": "value"}
        result_path = "test.json"

        # When
        service._save_to_json(result, result_path)

        # Then
        mock_open.assert_called_once_with(result_path, "w")
        mock_json_dump.assert_called_once_with(
            result, mock_open.return_value.__enter__(), indent=4
        )

    @pytest.mark.parametrize(
        "path, folder_name",
        [
            ("toto", "folder"),
            ("", "folder"),
        ],
    )
    def test_should_create_folder(
        self, path: str, folder_name: str, mock_path_mkdir: MagicMock
    ) -> None:
        # Given
        service = LocalResnapService(ConfigBuilder.a_config().build())

        # When
        service._create_folder(path, folder_name)

        # Then
        assert mock_path_mkdir.call_count == 1
