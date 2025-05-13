from typing import Any

import pytest
from pydantic import ValidationError

from resnap.boto.config import S3Config


class TestS3Config:
    @pytest.mark.parametrize(
        "config",
        [
            pytest.param(
                {"access_key": "key", "secret_key": "secret"}, id="missing bucket_name"
            ),
            pytest.param(
                {"access_key": "key", "bucket_name": "bucket"}, id="missing secret_key"
            ),
            pytest.param(
                {"secret_key": "secret", "bucket_name": "bucket"},
                id="missing access_key",
            ),
            pytest.param(
                {
                    "access_key": "key",
                    "secret_key": "secret",
                    "bucket_name": "bucket",
                    "force_path_style": "invalid",
                },
                id="invalid force_path_style type",
            ),
            pytest.param(
                {
                    "access_key": "key",
                    "secret_key": "secret",
                    "bucket_name": "bucket",
                    "signature_version": 123,
                },
                id="invalid signature_version type",
            ),
        ],
    )
    def test_s3_config_should_raise_validation_error(self, config: dict[str, Any]) -> None:
        # When / Then
        with pytest.raises(ValidationError):
            S3Config(**config)

    def test_s3_config_defaults(self) -> None:
        # Given
        config = {
            "access_key": "key",
            "secret_key": "secret",
            "bucket_name": "bucket",
        }

        # When
        s3_config = S3Config(**config)

        # Then
        assert s3_config.region_name is None
        assert s3_config.endpoint_url is None
        assert s3_config.force_path_style is True
        assert s3_config.signature_version == "s3v4"
