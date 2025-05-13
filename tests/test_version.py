from unittest.mock import patch

import pytest
from packaging.version import parse as parse_version

import resnap
from resnap.version import version_short


def test_standard_version():
    v = parse_version(resnap.VERSION)
    assert str(v) == resnap.VERSION


def test_version_attribute_is_present():
    assert hasattr(resnap, "__version__")


def test_version_attribute_is_a_string():
    assert isinstance(resnap.__version__, str)


@pytest.mark.parametrize("version, expected", (("2.1", "2.1"), ("2.1.0", "2.1")))
def test_version_short(version, expected):
    with patch("resnap.version.VERSION", version):
        assert version_short() == expected
