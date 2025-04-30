import re

import pytest

from resnap import factory
from resnap.settings import get_config_data
# from resnap.services.boto_service import BotoResnapService
from resnap.services.local_service import LocalResnapService


@pytest.fixture(autouse=True)
def reset_factory_globals() -> None:
    factory._resnap_config = get_config_data()


def test_should_raise_if_service_if_not_implemeted() -> None:
    # Given
    factory._resnap_config.save_to = "not_implemented"

    # When / Then
    with pytest.raises(
        NotImplementedError,
        match=re.escape("Resnap service not_implemented is not implemented")
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


# def test_should_return_boto_service() -> None:
#     # When
#     service = factory.ResnapServiceFactory.get_service()

#     # Then
#     assert isinstance(service, BotoResnapService)
