from unittest.mock import ANY, MagicMock

import pytest
from botocore.client import Config

from resnap.boto.config import S3Config
from resnap.boto.connection import get_s3_connection


def config_equal(config1: Config, config2: Config) -> bool:
    return (
        config1.signature_version == config2.signature_version
        and config1.s3 == config2.s3
        and config1.request_checksum_calculation == config2.request_checksum_calculation
        and config1.response_checksum_validation == config2.response_checksum_validation
    )


@pytest.fixture
def mock_s3_config() -> S3Config:
    return S3Config(
        access_key="test_access_key",
        secret_key="test_secret_key",
        bucket_name="test_bucket",
        region_name="test_region",
        endpoint_url="http://test-endpoint.com",
        signature_version="s3v4",
        force_path_style=True,
    )


@pytest.fixture
def mock_boto_client(mocker) -> MagicMock:
    return mocker.patch("resnap.boto.connection.boto3.client")


class TestS3Connection:
    def test_open_connection(self, monkeypatch, mock_boto_client: MagicMock, mock_s3_config: S3Config) -> None:
        # Given
        monkeypatch.setenv("REQUESTS_CA_BUNDLE", "/custom/path/to/ca.pem")
        expected_config = Config(
            signature_version=mock_s3_config.signature_version,
            s3={"addressing_style": "path"},
            request_checksum_calculation="when_required",
            response_checksum_validation="when_required",
        )

        # When
        connection = get_s3_connection(mock_s3_config)
        assert connection.is_open() is False
        connection.open()

        # Then
        mock_boto_client.assert_called_once_with(
            "s3",
            aws_access_key_id=mock_s3_config.access_key,
            aws_secret_access_key=mock_s3_config.secret_key,
            region_name=mock_s3_config.region_name,
            endpoint_url=mock_s3_config.endpoint_url,
            verify="/custom/path/to/ca.pem",
            config=ANY,
        )
        assert config_equal(expected_config, mock_boto_client.call_args.kwargs['config'])
        assert connection.is_open() is True

    def test_close_connection(self, mock_s3_config: S3Config) -> None:
        # Given
        connection = get_s3_connection(mock_s3_config)
        connection._connection = MagicMock()

        # When
        connection.close()

        # Then
        assert connection.is_open() is False

    def test_is_open(self, mock_s3_config: S3Config) -> None:
        # Given
        connection = get_s3_connection(mock_s3_config)
        connection._connection = MagicMock()
        assert connection.is_open() is True

        # When
        connection._connection = None

        # Then
        assert connection.is_open() is False

    def test_connection_property_with_already_connection(
        self, mock_boto_client: MagicMock, mock_s3_config: S3Config
    ) -> None:
        # Given
        connection = get_s3_connection(mock_s3_config)
        connection._connection = mock_boto_client

        # Then
        assert connection.connection == mock_boto_client

    def test_connection_property_without_connection(
        self, mock_boto_client: MagicMock, mock_s3_config: S3Config
    ) -> None:
        # Given
        connection = get_s3_connection(mock_s3_config)
        mock_client_instance = MagicMock()
        mock_boto_client.return_value = mock_client_instance

        # When
        con = connection.connection

        # Then
        mock_boto_client.assert_called_once()
        assert con == mock_client_instance

    def test_connection_property_setter(self, mock_s3_config: S3Config) -> None:
        # Given
        connection = get_s3_connection(mock_s3_config)

        # When / Then
        with pytest.raises(ValueError, match="The connection attribute is immutable."):
            connection.connection = MagicMock()

    def test_context_manager(self, mock_boto_client: MagicMock, mock_s3_config: S3Config) -> None:
        # Given
        mock_client_instance = MagicMock()
        mock_boto_client.return_value = mock_client_instance

        # When / Then
        with get_s3_connection(mock_s3_config) as conn:
            assert conn == mock_client_instance

    def test_context_manager_call_twice(self, mock_s3_config: S3Config) -> None:
        # Given
        connection = get_s3_connection(mock_s3_config)
        connection._connection = MagicMock()

        # When
        conn = connection._build_connection()

        # Then
        assert conn == connection._connection
        assert connection.is_open() is True
