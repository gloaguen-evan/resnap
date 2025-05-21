import re
import sys
from unittest.mock import MagicMock, patch

import pytest

from resnap import factory
from resnap.services.boto_service import BotoResnapService
from resnap.services.local_service import LocalResnapService
from resnap.services.service import ResnapService
from resnap.settings import get_config_data


@pytest.fixture(autouse=True)
def reset_factory_globals() -> None:
    factory._resnap_config = get_config_data()
    factory._service = None


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


def test_should_raise_if_service_if_not_implemeted() -> None:
    # Given
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
    factory._resnap_config.save_to = "s3"

    # When
    service = factory.ResnapServiceFactory.get_service()

    # Then
    assert isinstance(service, BotoResnapService)


@patch("importlib.util.find_spec", return_value=None)
@patch("resnap.services.boto_service.load_file", return_value=s3_secrets)
def test_should_raise_without_boto_extra(mock_find_spec: MagicMock, mock_load_file: MagicMock) -> None:
    # Given
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
