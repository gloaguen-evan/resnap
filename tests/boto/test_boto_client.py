import io
from unittest.mock import MagicMock, call, patch

import pandas as pd
import pytest
from botocore.exceptions import ClientError

from resnap.boto.client import S3Client
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
    return mock


@pytest.fixture
def mock_open(mocker) -> MagicMock:
    mock = mocker.patch("builtins.open")
    return mock


@pytest.fixture
def mock_s3_client(mock_s3_config: S3Config) -> S3Client:
    return S3Client(config=mock_s3_config)


@pytest.fixture
def mock_dataframe_handler(mocker) -> MagicMock:
    mock = mocker.patch("resnap.boto.client.get_dataframe_handler")
    return mock


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
    def test_should_upload_file(
        self,
        local_path_or_fileobj: str | io.FileIO | io.BytesIO,
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
    def test_should_download_file(
        self,
        local_path_or_fileobj: str | io.FileIO | io.BytesIO,
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

    @pytest.mark.parametrize("recursive", [True, False])
    @patch("resnap.boto.client.get_folders_and_files")
    def test_should_list_objects(
        self,
        mock_get_folders_and_files: MagicMock,
        recursive: bool,
        mock_s3_client: S3Client,
        mock_connection: MagicMock,
    ) -> None:
        # Given
        mock_connection.return_value.__enter__.return_value.get_paginator.return_value.paginate.return_value = [
            {"Contents": [{"Key": "file1.txt"}, {"Key": "file2.txt"}]}
        ]
        mock_get_folders_and_files.return_value = ([], ["file1.txt", "file2.txt"])
        expected_paginate_call = {
            "Bucket": mock_s3_client.config.bucket_name,
            "Prefix": "test/",
        }
        if not recursive:
            expected_paginate_call["Delimiter"] = "/"

        # When
        result = mock_s3_client.list_objects(remote_dir_path="test/", recursive=recursive)

        # Then
        assert result == ["file1.txt", "file2.txt"]
        mock_connection.return_value.__enter__.return_value.get_paginator.assert_called_once_with(
            "list_objects_v2"
        )
        mock_connection.return_value.__enter__.return_value.get_paginator.return_value.paginate.assert_called_once_with(
            **expected_paginate_call,
        )
        mock_get_folders_and_files.assert_called_once_with(
            "test/*", [{"Contents": [{"Key": "file1.txt"}, {"Key": "file2.txt"}]}]
        )

    def test_delete_object(self, mock_s3_client: S3Client, mock_connection: MagicMock) -> None:
        # When
        mock_s3_client.delete_object("file1.txt")

        # Then
        mock_connection.return_value.__enter__.return_value.delete_object.assert_called_once_with(
            Bucket="test_bucket", Key="file1.txt"
        )

    @pytest.mark.parametrize(
        "keys",
        [
            pytest.param(["file1.txt", "file2.txt"], id="multiple_keys"),
            pytest.param(["file1.txt"], id="single_key"),
        ],
    )
    def test_should_delete_objects(self, keys: list[str], mock_s3_client: S3Client, mock_connection: MagicMock) -> None:
        # Given
        expected_delete_call = {"Objects": [{"Key": key} for key in keys]}

        # When
        mock_s3_client.delete_objects(keys)

        # Then
        mock_connection.return_value.__enter__.return_value.delete_objects.assert_called_once_with(
            Bucket="test_bucket",
            Delete=expected_delete_call,
        )

    def test_should_delete_objects_empty(self, mock_s3_client: S3Client, mock_connection: MagicMock) -> None:
        # When
        mock_s3_client.delete_objects([])

        # Then
        mock_connection.return_value.__enter__.return_value.delete_objects.assert_not_called()

    @pytest.mark.parametrize(
        "remote_path",
        [
            pytest.param("test.txt", id="object_exists"),
            pytest.param("folder/", id="folder_exist"),
            pytest.param("/", id="bucket_exist"),
        ],
    )
    def test_should_return_true_if_object_exists(
        self,
        remote_path: str,
        mock_s3_client: S3Client,
        mock_connection: MagicMock,
    ) -> None:
        # When
        result = mock_s3_client.object_exists(remote_path)

        # Then
        assert result is True
        if remote_path == "/":
            mock_connection.return_value.__enter__.return_value.get_bucket_acl.assert_called_once_with(
                Bucket="test_bucket"
            )
        elif remote_path.endswith("/"):
            mock_connection.return_value.__enter__.return_value.get_object.assert_called_once_with(
                Bucket="test_bucket", Key=remote_path
            )
        else:
            mock_connection.return_value.__enter__.return_value.head_object.assert_called_once_with(
                Bucket="test_bucket", Key=remote_path
            )

    def test_should_raise_if_object_not_exists(self, mock_s3_client: S3Client, mock_connection: MagicMock) -> None:
        # Given
        mock_connection.return_value.__enter__.return_value.head_object.side_effect = ClientError(
            {"Error": {"Code": "404"}}, "HeadObject"
        )

        # When
        result = mock_s3_client.object_exists("file1.txt")

        # Then
        assert result is False

    @pytest.mark.parametrize(
        "path",
        [
            pytest.param("test/dir", id="dir_path"),
            pytest.param("test/dir/", id="dir_path_with_slash"),
        ],
    )
    def test_should_create_dir(self, path: str, mock_s3_client: S3Client, mock_connection: MagicMock) -> None:
        # When
        mock_s3_client.mkdir(path)

        # Then
        mock_connection.return_value.__enter__.return_value.upload_fileobj.assert_called_once()

    def test_should_return_df_from_file(
        self,
        mock_s3_client: S3Client,
        mock_connection: MagicMock,
        mock_dataframe_handler: MagicMock,
    ) -> None:
        # Given
        mock_dataframe_handler.return_value.read_df.return_value = MagicMock()
        mock_connection.return_value.__enter__.return_value.get_object.return_value = {
            "Body": MagicMock(read=MagicMock(return_value=b"col1,col2\n1,2\n3,4"))
        }

        # When
        with patch.object(S3Client, "object_exists", return_value=True):
            result = mock_s3_client.get_df_from_file("test.csv", "csv", compression="gzip", nrows=10)

        # Then
        assert result == mock_dataframe_handler.return_value.read_df.return_value
        mock_connection.return_value.__enter__.return_value.get_object.assert_called_once_with(
            Bucket="test_bucket", Key="test.csv"
        )
        mock_dataframe_handler.return_value.read_df.assert_called_once_with(
            mock_connection.return_value.__enter__.return_value.get_object.return_value["Body"],
            compression="gzip",
            nrows=10,
        )

    def test_should_raise_if_file_not_exists(self, mock_s3_client: S3Client, mock_dataframe_handler: MagicMock) -> None:
        # When / Then
        with pytest.raises(FileNotFoundError, match="File test.csv not exists in bucket test_bucket"):
            with patch.object(S3Client, "object_exists", return_value=False):
                mock_s3_client.get_df_from_file("test.csv", "csv")

    @pytest.mark.parametrize(
        "compression, file_format, expected_compression",
        [
            pytest.param(None, "csv", None, id="no_compression"),
            pytest.param("gzip", "csv", "gzip", id="gzip_compression"),
            pytest.param(None, "parquet", "snappy", id="snappy_compression"),
        ],
    )
    def test_should_push_df_to_file(
        self,
        compression: str | None,
        file_format: str,
        expected_compression: str | None,
        mock_s3_client: S3Client,
        mock_dataframe_handler: MagicMock,
    ) -> None:
        # Given
        df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        expected_write_df_return = b"col1,col2\n1,2\n3,4"
        mock_dataframe_handler.return_value.write_df.return_value = expected_write_df_return

        # When / Then
        with patch.object(S3Client, "upload_file") as mock_upload_file:
            if compression:
                mock_s3_client.push_df_to_file(df, "test.csv", compression=compression, file_format=file_format)
            else:
                mock_s3_client.push_df_to_file(df, "test.csv", file_format=file_format)
            mock_dataframe_handler.return_value.write_df.assert_called_once_with(
                df, compression=expected_compression
            )
            mock_upload_file.assert_called_once_with(expected_write_df_return, "test.csv")

    def test_should_rmdir(self, mock_s3_client: S3Client, mock_connection: MagicMock) -> None:
        # Given
        mock_s3_client.list_folders_and_files = MagicMock(return_value=(["folder1/", "folder2/"], ["file1.txt"]))
        mock_s3_client.delete_objects = MagicMock()

        # When
        mock_s3_client.rmdir("test/")

        # Then
        assert mock_s3_client.delete_objects.call_count == 2
        calls = [
            call(["file1.txt"]),
            call(["folder1/", "folder2/"]),
        ]
        mock_s3_client.delete_objects.assert_has_calls(calls)
