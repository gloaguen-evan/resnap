from typing import Any

import pytest
from pydantic import ValidationError

from resnap.helpers.config import Config, Services


class TestServices:
    def test_services(self) -> None:
        assert Services.LOCAL == "local"


class TestConfig:
    @pytest.mark.parametrize(
        "config",
        [
            pytest.param({"save_to": Services.LOCAL}, id="missing enabled"),
            pytest.param(
                {"save_to": Services.LOCAL, "enabled": 5}, id="wrong enabled type"
            ),
            pytest.param({"enabled": True, "save_to": "test"}, id="unknown save_to"),
            pytest.param(
                {"enabled": True, "save_to": Services.LOCAL, "output_base_path": 25},
                id="wrong output_base_path type",
            ),
            pytest.param(
                {"enabled": True, "save_to": Services.LOCAL, "secrets_file_name": 25},
                id="wrong secrets_file_name type",
            ),
            pytest.param(
                {
                    "enabled": True,
                    "save_to": Services.LOCAL,
                    "enable_remove_old_files": "test",
                },
                id="wrong enable_remove_old_files type",
            ),
            pytest.param(
                {
                    "enabled": True,
                    "save_to": Services.LOCAL,
                    "max_history_files_length": "test",
                },
                id="wrong max_history_files_length type",
            ),
            pytest.param(
                {
                    "enabled": True,
                    "save_to": Services.LOCAL,
                    "max_history_files_length": -5,
                },
                id="wrong max_history_files_length value",
            ),
            pytest.param(
                {
                    "enabled": True,
                    "save_to": Services.LOCAL,
                    "max_history_files_time_unit": 5,
                },
                id="wrong max_history_files_time_unit type",
            ),
            pytest.param(
                {
                    "enabled": True,
                    "save_to": Services.LOCAL,
                    "max_history_files_time_unit": "test",
                },
                id="wrong max_history_files_time_unit value",
            ),
        ],
    )
    def test_should_failed_with_wrong_config(self, config: dict[str, Any]) -> None:
        # When
        with pytest.raises(ValueError):
            Config(**config)

    def test_should_raise_if_not_secrets_file_name_and_save_to_is_boto(self) -> None:
        # When / Then
        with pytest.raises(ValidationError, match="secrets_file_name is required when save_to is s3"):
            Config(enabled=True, save_to=Services.S3)

    def test_should_build_and_check_config_successfully(self) -> None:
        # Given
        input_config = {
            "enabled": True,
            "save_to": Services.S3,
            "output_base_path": "",
            "secrets_file_name": "test",
            "enable_remove_old_files": True,
            "max_history_files_length": 5,
            "max_history_files_time_unit": "day",
        }
        # When
        config = Config(**input_config)

        # Then
        assert input_config == config.model_dump()
