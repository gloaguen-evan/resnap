import pytest

from resnap import factory
from resnap.helpers.singleton import SingletonABCMeta


@pytest.fixture(autouse=True)
def reset_singleton() -> None:
    SingletonABCMeta._instances.clear()


@pytest.fixture(autouse=True)
def reset_factory_globals() -> None:
    factory._resnap_config = None
    factory._service = None
