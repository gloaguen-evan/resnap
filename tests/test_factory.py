import re
import sys
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
import pytest_mock

from resnap import factory
from resnap.helpers.config import Config, Services
from resnap.helpers.time_utils import TimeUnit
from resnap.services.boto_service import BotoResnapService
from resnap.services.local_service import LocalResnapService
from resnap.services.service import ResnapService

fake_config_toml = """
[tool.resnap]
enabled = true
save_to = "s3"
output_base_path = "output"
secrets_file_name = "my-secret.yml"
enable_remove_old_files = false
max_history_files_length = 10
max_history_files_time_unit = "day"
"""


@pytest.fixture
def fake_config() -> Config:
    return Config(
        enabled=True,
        save_to=Services.S3,
        output_base_path="output",
        secrets_file_name="my-secret.yml",
        enable_remove_old_files=False,
        max_history_files_length=10,
        max_history_files_time_unit=TimeUnit.DAY,
    )


@pytest.fixture
def mock_custom_config_location(tmp_path: Path, mocker: pytest_mock.MockFixture) -> Generator[None, None, None]:
    fake_config_path = tmp_path / "pyproject.toml"
    fake_config_path.write_text(fake_config_toml)
    mocker.patch.dict(
        "os.environ",
        {"RESNAP_CONFIG_FILE": str(fake_config_path)},
    )
    yield
    mocker.patch.dict("os.environ", clear=True)


def test_get_config_test_should_read_config_from_custom_location(
    mock_custom_config_location: Generator[None, None, None],
    fake_config: Config,
) -> None:
    # When
    res = factory.get_config()

    # Then
    assert res == fake_config


def test_should_set_service() -> None:
    # Given
    custom_service = MagicMock(spec=ResnapService, name="CustomResnapService")

    # When
    factory.set_resnap_service(custom_service)

    # Then
    assert factory._service == custom_service
    assert isinstance(factory._service, ResnapService)


def test_should_not_set_service_if_not_resnap_service() -> None:
    # Given
    custom_service = MagicMock(name="CustomResnapService")

    # When / Then
    with pytest.raises(
        TypeError,
        match=re.escape(f"Expected ResnapService, got {type(custom_service)}"),
    ):
        factory.set_resnap_service(custom_service)


def test_should_raise_if_service_if_not_implemented() -> None:
    # Given
    factory.get_config()  # enforce the first load
    factory._resnap_config.save_to = "not_implemented"

    # When / Then
    with pytest.raises(
        NotImplementedError,
        match=re.escape("Resnap service not_implemented is not implemented"),
    ):
        factory.ResnapServiceFactory.get_service()


def test_should_return_local_service() -> None:
    # When
    service = factory.ResnapServiceFactory.get_service()

    # Then
    assert isinstance(service, LocalResnapService)


def test_should_return_same_instance_if_called_two_times() -> None:
    # When
    service_1 = factory.ResnapServiceFactory.get_service()
    service_2 = factory.ResnapServiceFactory.get_service()

    # Then
    assert service_1 == service_2


s3_secrets = {
    "access_key": "toto",
    "secret_key": "toto",
    "bucket_name": "toto",
}


@patch("importlib.util.find_spec", return_value=True)
@patch("resnap.services.boto_service.load_file", return_value=s3_secrets)
def test_should_return_boto_service_with_boto_extra(mock_find_spec: MagicMock, mock_load_file: MagicMock) -> None:
    # Given
    factory.get_config()  # enforce the first load
    factory._resnap_config.save_to = "s3"

    # When
    service = factory.ResnapServiceFactory.get_service()

    # Then
    assert isinstance(service, BotoResnapService)


@patch("importlib.util.find_spec", return_value=None)
@patch("resnap.services.boto_service.load_file", return_value=s3_secrets)
def test_should_raise_without_boto_extra(mock_find_spec: MagicMock, mock_load_file: MagicMock) -> None:
    # Given
    factory.get_config()  # enforce the first load
    factory._resnap_config.save_to = "s3"

    if "resnap.services.boto_service" in sys.modules:
        del sys.modules["resnap.boto"]
        del sys.modules["resnap.services.boto_service"]

    # When / Then
    with pytest.raises(
        ImportError,
        match=re.escape("Please install the boto extra to save to S3: `pip install resnap[boto]`"),
    ):
        factory.ResnapServiceFactory.get_service()
