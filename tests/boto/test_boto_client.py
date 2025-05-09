import io
from typing import Union
import pytest
from unittest.mock import MagicMock, patch
from resnap.boto.client import S3Client, format_remote_path
from resnap.boto.config import S3Config


@pytest.fixture
def mock_s3_config() -> S3Config:
    return S3Config(
        access_key="test_access_key",
        secret_key="test_secret_key",
        bucket_name="test_bucket",
        region_name="test_region",
        endpoint_url="http://test-endpoint.com",
    )


@pytest.fixture
def mock_connection(mocker) -> MagicMock:
    mock = mocker.patch("resnap.boto.client.get_s3_connection")
    mock.return_value.__enter__.return_value = MagicMock()
    return mock


@pytest.fixture
def mock_open(mocker) -> MagicMock:
    mock = mocker.patch("builtins.open")
    return mock


@pytest.fixture
def mock_s3_client(mock_s3_config: S3Config) -> S3Client:
    return S3Client(config=mock_s3_config)


class TestS3Client:
    @pytest.mark.parametrize(
        "local_path_or_fileobj",
        [
            pytest.param(
                "test.txt",
                id="file_path",
            ),
            pytest.param(
                MagicMock(spec=io.FileIO),
                id="file_io",
            ),
            pytest.param(
                MagicMock(spec=io.BytesIO),
                id="bytes_io",
            ),
        ],
    )
    def test_upload_file(
        self,
        local_path_or_fileobj: Union[str, io.FileIO, io.BytesIO],
        mock_s3_client: S3Client,
        mock_connection: MagicMock,
        mock_open: MagicMock,
    ) -> None:
        # Given
        if isinstance(local_path_or_fileobj, str):
            expected_fileobj = MagicMock()
            mock_open.return_value.__enter__.return_value = expected_fileobj
        else:
            expected_fileobj = local_path_or_fileobj

        # When
        mock_s3_client.upload_file(local_path_or_fileobj, "remote/test.txt")

        # Then
        mock_connection.return_value.__enter__.return_value.upload_fileobj.assert_called_once_with(
            expected_fileobj,
            mock_s3_client.config.bucket_name,
            "remote/test.txt",
        )

    @pytest.mark.parametrize(
        "local_path_or_fileobj",
        [
            pytest.param(
                "test.txt",
                id="file_path",
            ),
            pytest.param(
                MagicMock(spec=io.FileIO),
                id="file_io",
            ),
            pytest.param(
                MagicMock(spec=io.BytesIO),
                id="bytes_io",
            ),
        ],
    )
    def test_download_file(
        self,
        local_path_or_fileobj: Union[str, io.FileIO, io.BytesIO],
        mock_connection: MagicMock,
        mock_s3_client: S3Client,
        mock_open: MagicMock,
    ) -> None:
        # Given
        if isinstance(local_path_or_fileobj, str):
            expected_fileobj = MagicMock()
            mock_open.return_value.__enter__.return_value = expected_fileobj
        else:
            expected_fileobj = local_path_or_fileobj

        # When
        mock_s3_client.download_file(local_path_or_fileobj, "remote/test.txt")

        # Then
        mock_connection.return_value.__enter__.return_value.download_fileobj.assert_called_once_with(
            mock_s3_client.config.bucket_name,
            "remote/test.txt",
            expected_fileobj,
        )

    # def test_list_objects(mock_s3_client):
    #     mock_s3_client.s3.list_objects_v2.return_value = {
    #         "Contents": [{"Key": "file1.txt"}, {"Key": "file2.txt"}]
    #     }
    #     result = mock_s3_client.list_objects(prefix="test/")
    #     assert result == ["file1.txt", "file2.txt"]

    # def test_delete_object(mock_s3_client):
    #     mock_s3_client.delete_object("file1.txt")
    #     mock_s3_client.s3.delete_object.assert_called_once_with(
    #         Bucket="test-bucket", Key="file1.txt"
    #     )

    # def test_delete_objects(mock_s3_client):
    #     mock_s3_client.delete_objects(["file1.txt", "file2.txt"])
    #     mock_s3_client.s3.delete_objects.assert_called_once_with(
    #         Bucket="test-bucket",
    #         Delete={"Objects": [{"Key": "file1.txt"}, {"Key": "file2.txt"}]},
    #     )

    # def test_object_exists(mock_s3_client):
    #     mock_s3_client.s3.head_object.return_value = {}
    #     assert mock_s3_client.object_exists("file1.txt") is True

    #     mock_s3_client.s3.head_object.side_effect = ClientError(
    #         {"Error": {"Code": "404"}}, "HeadObject"
    #     )
    #     assert mock_s3_client.object_exists("file1.txt") is False

    # @patch("resnap.boto.client.get_s3_connection")
    # def test_mkdir(mock_get_s3_connection, mock_s3_client):
    #     mock_connection = MagicMock()
    #     mock_get_s3_connection.return_value.__enter__.return_value = mock_connection

    #     mock_s3_client.mkdir("test/dir")
    #     mock_connection.upload_fileobj.assert_called_once()

    # @patch("resnap.boto.client.pd.read_csv")
    # def test_get_df_from_file_csv(mock_read_csv, mock_s3_client):
    #     mock_read_csv.return_value = "mock_dataframe"
    #     result = mock_s3_client.get_df_from_file("test.csv", "csv")
    #     assert result == "mock_dataframe"
    #     mock_read_csv.assert_called_once_with("test.csv")

    # @patch("resnap.boto.client.pd.read_parquet")
    # def test_get_df_from_file_parquet(mock_read_parquet, mock_s3_client):
    #     mock_read_parquet.return_value = "mock_dataframe"
    #     result = mock_s3_client.get_df_from_file("test.parquet", "parquet")
    #     assert result == "mock_dataframe"
    #     mock_read_parquet.assert_called_once_with("test.parquet")

    # @patch("resnap.boto.client.pd.DataFrame.to_csv")
    # def test_push_df_to_file_csv(mock_to_csv, mock_s3_client):
    #     df = MagicMock()
    #     mock_s3_client.push_df_to_file(df, "test.csv", "csv")
    #     mock_to_csv.assert_called_once_with("test.csv", index=False)

    # @patch("resnap.boto.client.pd.DataFrame.to_parquet")
    # def test_push_df_to_file_parquet(mock_to_parquet, mock_s3_client):
    #     df = MagicMock()
    #     mock_s3_client.push_df_to_file(df, "test.parquet", "parquet")
    #     mock_to_parquet.assert_called_once_with("test.parquet", index=False)

    # def test_push_to_file_json(mock_s3_client):
    #     data = {"key": "value"}
    #     with patch.object(mock_s3_client, "upload_file") as mock_upload_file:
    #         mock_s3_client.push_to_file(data, "test.json", "json")
    #         mock_upload_file.assert_called_once()

    # def test_push_to_file_text(mock_s3_client):
    #     data = "test data"
    #     with patch.object(mock_s3_client, "upload_file") as mock_upload_file:
    #         mock_s3_client.push_to_file(data, "test.txt", "text")
    #         mock_upload_file.assert_called_once()

    # def test_format_remote_path():
    #     assert format_remote_path("/test/path") == "test/path"
    #     assert format_remote_path("test/path") == "test/path"
