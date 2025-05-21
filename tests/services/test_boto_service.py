import json
import pickle
from datetime import datetime
from unittest.mock import ANY, MagicMock

import pandas as pd
import pytest

from resnap.helpers.metadata import Metadata, MetadataSuccess
from resnap.helpers.status import Status
from resnap.helpers.utils import hash_arguments
from resnap.services.boto_service import BotoResnapService
from tests.builders.config_builder import ConfigBuilder

s3_secrets: dict = {
    "endpoint_url": "http://s3-server",
    "access_key": "access_key",
    "secret_key": "secret_key",
    "bucket_name": "bucket",
}


@pytest.fixture(autouse=True)
def mock_load_file(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch(
        "resnap.services.boto_service.load_file", return_value=s3_secrets
    )
    return mock


@pytest.fixture
def mock_s3_client_object_exists(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch("resnap.services.boto_service.S3Client.object_exists")
    return mock


@pytest.fixture
def mock_s3_client_list_objects(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch("resnap.services.boto_service.S3Client.list_objects")
    return mock


@pytest.fixture
def mock_s3_client_delete_objects(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch("resnap.services.boto_service.S3Client.delete_objects")
    return mock


@pytest.fixture
def mock_s3_client_download_file(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch("resnap.services.boto_service.S3Client.download_file")
    return mock


@pytest.fixture
def mock_s3_client_upload_file(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch("resnap.services.boto_service.S3Client.upload_file")
    return mock


@pytest.fixture
def mock_s3_client_push_df_to_file(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch("resnap.services.boto_service.S3Client.push_df_to_file")
    return mock


@pytest.fixture
def mock_s3_client_get_df_from_file(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch("resnap.services.boto_service.S3Client.get_df_from_file")
    return mock


@pytest.fixture
def mock_s3_client_mkdir(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch("resnap.services.boto_service.S3Client.mkdir")
    return mock


@pytest.fixture
def mock_read_metadata(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch("resnap.services.boto_service.BotoResnapService._read_metadata")
    return mock


class TestBotoService:
    @pytest.mark.parametrize(
        "path, expected",
        [
            ("folder/", "folder/"),
            ("folder", "folder/"),
        ],
    )
    def test_should_format_path(self, path: str, expected: str) -> None:
        # When
        result = BotoResnapService._format_path(path)

        # Then
        assert result == expected

    @pytest.mark.parametrize(
        "file_path, is_deleted",
        [
            ("test_2021-01-01T00-00-00.resnap", True),
            ("test_2021-01-01T00-00-00.resnap.pkl", True),
            ("toto/toto_2021-01-01T00-00-00.csv", False),
            (f"test_{datetime.now().isoformat().replace(':', '-')}.resnap", False),
        ],
    )
    def test_should_clear_old_saves_files(
        self,
        file_path: str,
        is_deleted: bool,
        mock_s3_client_object_exists: MagicMock,
        mock_s3_client_list_objects: MagicMock,
        mock_s3_client_delete_objects: MagicMock,
    ) -> None:
        # Given
        mock_s3_client_object_exists.return_value = True
        mock_s3_client_list_objects.return_value = [file_path]
        service = BotoResnapService(ConfigBuilder.a_config().build())

        # When
        service.clear_old_saves()

        # Then
        mock_s3_client_list_objects.assert_called_once()
        assert mock_s3_client_delete_objects.call_count == int(is_deleted)

    @pytest.mark.parametrize(
        "file_path, is_empty, is_deleted",
        [
            ("toto/", False, False),
            ("toto/", True, True),
        ],
    )
    def test_should_clear_old_saves_folders(
        self,
        file_path: str,
        is_empty: bool,
        is_deleted: bool,
        mock_s3_client_object_exists: MagicMock,
        mock_s3_client_list_objects: MagicMock,
        mock_s3_client_delete_objects: MagicMock,
    ) -> None:
        # Given
        side_effects = [[file_path]]
        if is_empty:
            side_effects.append([])
        else:
            side_effects.append(["test.csv"])
        mock_s3_client_list_objects.side_effect = side_effects
        mock_s3_client_object_exists.return_value = True
        service = BotoResnapService(ConfigBuilder.a_config().build())

        # When
        service.clear_old_saves()

        # Then
        assert mock_s3_client_list_objects.call_count == 2
        assert mock_s3_client_delete_objects.call_count == int(is_deleted)

    def test_should_not_clear_old_saves_if_folder_does_not_exist(
        self,
        mock_s3_client_object_exists: MagicMock,
        mock_s3_client_list_objects: MagicMock,
    ) -> None:
        # Given
        mock_s3_client_object_exists.return_value = False
        service = BotoResnapService(ConfigBuilder.a_config().build())

        # When
        service.clear_old_saves()

        # Then
        mock_s3_client_list_objects.assert_not_called()

    def test_should_read_metadata(self, mock_s3_client_download_file: MagicMock) -> None:
        # Given
        service = BotoResnapService(ConfigBuilder.a_config().build())
        expected_metadata = MetadataSuccess(
            status=Status.SUCCESS,
            event_time=datetime.fromisoformat("2021-01-01T00:00:00"),
            result_path="test_2021-01-01T00-00-00.resnap.pkl",
            result_type="str",
            hashed_arguments=hash_arguments({"test": "toto"}),
            extra_metadata={},
        )
        mock_s3_client_download_file.side_effect = lambda buffer, path: buffer.write(
            json.dumps(expected_metadata.to_dict()).encode()
        )

        # When
        result = service._read_metadata("tests/data/metadata/test-metadata_2021-01-01T00-00-00.resnap")

        # Then
        assert isinstance(result, Metadata)
        assert result == expected_metadata

    def test_should_return_metadatas(
        self,
        mock_s3_client_list_objects: MagicMock,
        mock_read_metadata: MagicMock,
    ) -> None:
        # Given
        service = BotoResnapService(ConfigBuilder.a_config().build())
        mock_s3_client_list_objects.return_value = [
            "test-metadata_2021-01-01T00-00-00.resnap",
            "test-metadata_2024-01-01T00-00-00.resnap",
            "toto",
            "toto_2021-01-02T00-00-00.resnap",
            "test.csv",
        ]
        expected_metadatas = [
            MetadataSuccess(
                status=Status.SUCCESS,
                event_time=datetime.fromisoformat("2024-01-01T00:00:00"),
                result_path="test_2024-01-01T00-00-00.resnap.pkl",
                result_type="str",
                hashed_arguments=hash_arguments({}),
            ),
            MetadataSuccess(
                status=Status.SUCCESS,
                event_time=datetime.fromisoformat("2021-01-01T00:00:00"),
                result_path="test_2021-01-01T00-00-00.resnap.pkl",
                result_type="str",
                hashed_arguments=hash_arguments({}),
            ),
        ]
        mock_read_metadata.side_effect = expected_metadatas

        # When
        result = service.get_success_metadatas("test", "")

        # Then
        assert result == expected_metadatas
        assert len(result) == 2

    def test_should_return_none_if_not_metadata(self, mock_s3_client_list_objects: MagicMock) -> None:
        # Given
        service = BotoResnapService(ConfigBuilder.a_config().build())
        mock_s3_client_list_objects.return_value = []

        # When
        result = service.get_success_metadatas("test", "")

        # Then
        assert len(result) == 0

    def test_should_write_metadata(self, mock_s3_client_upload_file: MagicMock) -> None:
        # Given
        service = BotoResnapService(ConfigBuilder.a_config().build())
        metadata = MetadataSuccess(
            status=Status.SUCCESS,
            event_time=datetime.fromisoformat("2021-01-01T00:00:00"),
            result_path="test_2021-01-01T00-00-00.resnap.pkl",
            result_type="str",
            hashed_arguments=hash_arguments({"test": "toto"}),
        )
        mock_s3_client_upload_file.side_effect = lambda buffer, path: buffer.write(
            json.dumps(metadata.to_dict()).encode()
        )

        # When
        service._write_metadata("test_2021-01-01T00-00-00.resnap", metadata)

        # Then
        mock_s3_client_upload_file.assert_called_once()
        args, _ = mock_s3_client_upload_file.call_args
        assert args[1] == "test_2021-01-01T00-00-00.resnap"

    def test_should_save_dataframe_to_parquet(self, mock_s3_client_push_df_to_file: MagicMock) -> None:
        # Given
        service = BotoResnapService(ConfigBuilder.a_config().build())
        result = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        result_path = "test.parquet"

        # When
        service._save_dataframe_to_parquet(result, result_path)

        # Then
        mock_s3_client_push_df_to_file.assert_called_once_with(
            result, "test.parquet", compression="gzip", file_format="parquet"
        )

    def test_should_save_dataframe_to_csv(self, mock_s3_client_push_df_to_file: MagicMock) -> None:
        # Given
        service = BotoResnapService(ConfigBuilder.a_config().build())
        result = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        result_path = "test.csv"

        # When
        service._save_dataframe_to_csv(result, result_path)

        # Then
        mock_s3_client_push_df_to_file.assert_called_once_with(result, "test.csv", file_format="csv")

    def test_should_save_to_pickle(self, mock_s3_client_upload_file: MagicMock) -> None:
        # Given
        service = BotoResnapService(ConfigBuilder.a_config().build())
        result = {"key": "value"}
        result_path = "test.pkl"

        # When
        service._save_to_pickle(result, result_path)

        # Then
        mock_s3_client_upload_file.assert_called_once()
        args, _ = mock_s3_client_upload_file.call_args
        assert args[1] == "test.pkl"

    def test_should_save_to_text(self, mock_s3_client_upload_file: MagicMock) -> None:
        # Given
        service = BotoResnapService(ConfigBuilder.a_config().build())
        result = "toto"
        result_path = "test.txt"

        # When
        service._save_to_text(result, result_path)

        # Then
        mock_s3_client_upload_file.assert_called_once()
        args, _ = mock_s3_client_upload_file.call_args
        assert args[1] == "test.txt"

    def test_should_save_to_json(self, mock_s3_client_upload_file: MagicMock) -> None:
        # Given
        service = BotoResnapService(ConfigBuilder.a_config().build())
        result = {"key": "value"}
        result_path = "test.json"

        # When
        service._save_to_json(result, result_path)

        # Then
        mock_s3_client_upload_file.assert_called_once()
        args, _ = mock_s3_client_upload_file.call_args
        assert args[1] == "test.json"

    def test_should_read_parquet_to_dataframe(self, mock_s3_client_get_df_from_file: MagicMock) -> None:
        # Given
        service = BotoResnapService(ConfigBuilder.a_config().build())
        file_path = "test.parquet"
        expected_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_s3_client_get_df_from_file.return_value = expected_df

        # When
        result = service._read_parquet_to_dataframe(file_path)

        # Then
        pd.testing.assert_frame_equal(result, expected_df)
        mock_s3_client_get_df_from_file.assert_called_once_with("test.parquet", file_format="parquet")

    def test_should_read_csv_to_dataframe(self, mock_s3_client_get_df_from_file: MagicMock) -> None:
        # Given
        service = BotoResnapService(ConfigBuilder.a_config().build())
        file_path = "test.csv"
        expected_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        mock_s3_client_get_df_from_file.return_value = expected_df

        # When
        result = service._read_csv_to_dataframe(file_path)

        # Then
        pd.testing.assert_frame_equal(result, expected_df)
        mock_s3_client_get_df_from_file.assert_called_once_with("test.csv", file_format="csv")

    def test_should_read_pickle(self, mock_s3_client_download_file: MagicMock) -> None:
        # Given
        service = BotoResnapService(ConfigBuilder.a_config().build())
        file_path = "test.pkl"
        expected_data = {"key": "value"}
        mock_s3_client_download_file.side_effect = lambda buffer, path: buffer.write(pickle.dumps(expected_data))

        # When
        result = service._read_pickle(file_path)

        # Then
        assert result == expected_data
        mock_s3_client_download_file.assert_called_once_with(ANY, str(file_path))

    def test_should_read_text(self, mock_s3_client_download_file: MagicMock) -> None:
        # Given
        service = BotoResnapService(ConfigBuilder.a_config().build())
        file_path = "test.txt"
        expected_data = "toto"
        mock_s3_client_download_file.side_effect = lambda buffer, path: buffer.write(expected_data.encode())

        # When
        result = service._read_text(file_path)

        # Then
        assert result == expected_data
        mock_s3_client_download_file.assert_called_once_with(ANY, str(file_path))

    def test_should_read_json(self, mock_s3_client_download_file: MagicMock) -> None:
        # Given
        service = BotoResnapService(ConfigBuilder.a_config().build())
        file_path = "test.json"
        expected_data = {"key": "value"}
        mock_s3_client_download_file.side_effect = (
            lambda buffer, path: buffer.write(json.dumps(expected_data, indent=4).encode())
        )

        # When
        result = service._read_json(file_path)

        # Then
        assert result == expected_data
        mock_s3_client_download_file.assert_called_once_with(ANY, str(file_path))

    @pytest.mark.parametrize(
        "path, is_exists_path, folder_name, is_exists_folder, exist_count, mkdir_count",
        [
            ("toto", False, "folder", False, 2, 2),
            ("toto", True, "folder", False, 2, 1),
            ("toto", True, "folder", True, 2, 0),
            ("toto", False, "", False, 1, 1),
            ("toto", True, "", False, 1, 0),
            ("", False, "folder", False, 1, 1),
            ("", False, "folder", True, 1, 0),
        ],
    )
    def test_should_create_folder(
        self,
        path: str,
        is_exists_path: bool,
        folder_name: str,
        is_exists_folder: bool,
        exist_count: int,
        mkdir_count: int,
        mock_s3_client_mkdir: MagicMock,
        mock_s3_client_object_exists: MagicMock,
    ) -> None:
        # Given
        service = BotoResnapService(ConfigBuilder.a_config().build())
        side_effects = []
        if path:
            side_effects.append(is_exists_path)
        if folder_name:
            side_effects.append(is_exists_folder)
        mock_s3_client_object_exists.side_effect = side_effects

        # When
        service._create_folder(path, folder_name)

        # Then
        assert mock_s3_client_object_exists.call_count == exist_count
        assert mock_s3_client_mkdir.call_count == mkdir_count
