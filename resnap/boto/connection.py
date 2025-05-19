import boto3
from botocore.client import BaseClient, Config

from ..helpers.ssl import get_ca_bundle_path
from .config import S3Config


class get_s3_connection:
    """Open a new S3 connection.

    Use this function as a context manager:
        with get_s3_connection(...) as con:
            ...

    Args:
        config (S3Config): S3 configuration object.
    """

    def __init__(self, config: S3Config) -> None:
        self._config = config
        self._connection: BaseClient | None = None

    def open(self) -> None:
        """Open S3 connection."""
        self._connection = boto3.client(
            "s3",
            aws_access_key_id=self._config.access_key,
            aws_secret_access_key=self._config.secret_key,
            region_name=self._config.region_name,
            endpoint_url=self._config.endpoint_url,
            verify=get_ca_bundle_path() if not self._config.cert_file_path else self._config.cert_file_path,
            config=Config(
                signature_version=self._config.signature_version,
                s3={"addressing_style": "path" if self._config.force_path_style else "virtual"},
                request_checksum_calculation="when_required",
                response_checksum_validation="when_required",
            ),
        )

    def close(self) -> None:
        """Close ceph connection."""
        if self._connection:
            self._connection = None

    def is_open(self) -> bool:
        """Chek if connection is open."""
        return bool(self._connection)

    @property
    def connection(self) -> BaseClient:
        if self._connection:
            return self._connection

        return self._build_connection()

    @connection.setter
    def connection(self, _) -> None:
        raise ValueError("The connection attribute is immutable.")

    def _build_connection(self) -> BaseClient:
        if self._connection:
            return self._connection
        self.open()
        return self._connection

    def __enter__(self) -> BaseClient:
        self._build_connection()
        return self._connection

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
