import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from resnap.helpers.config import Config
from resnap.settings import get_config_data, get_config_file_path


@pytest.fixture
def mock_os_listdir(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch("os.listdir")
    return mock


@pytest.fixture(autouse=True)
def mock_os_getcwd(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch("os.getcwd", return_value="tests")
    return mock


@pytest.fixture
def mock_get_config_file_path(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch("resnap.settings.get_config_file_path")
    return mock


@pytest.fixture(autouse=True)
def mock_toml_load(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch("toml.load")
    return mock


@pytest.mark.parametrize(
    "file_path, config_data, expected",
    [
        pytest.param(
            "tests/pyproject.toml",
            {"tool": {"resnap": {"enabled": True, "output_base_path": "resnap"}}},
            Config(enabled=True, output_base_path="resnap"),
            id="find config in pyproject.toml",
        ),
        pytest.param(
            "tests/pyproject.toml",
            {"toto": {"test": True}},
            Config(enabled=True),
            id="don't find tool config in pyproject.toml",
        ),
        pytest.param(
            "tests/pyproject.toml",
            {"tool": {"test": True}},
            Config(enabled=True),
            id="don't find resnap config in pyproject.toml",
        ),
    ],
)
def test_should_get_config_data(
    file_path: str,
    config_data: dict,
    expected: Config,
    mock_get_config_file_path: MagicMock,
    mock_toml_load: MagicMock,
) -> None:
    # Given
    mock_get_config_file_path.return_value = file_path
    mock_toml_load.return_value = config_data

    # When
    config = get_config_data()

    # Then
    assert isinstance(config, Config)
    assert config == expected


def test_should_not_call_get_config_file_path_if_file_path_is_provided(
    mock_get_config_file_path: MagicMock, mock_toml_load: MagicMock,
) -> None:
    # Given
    file_path = "tests/pyproject.toml"
    mock_toml_load.return_value = {"tool": {"resnap": {"enabled": True, "output_base_path": "resnap"}}}
    expected = Config(enabled=True, output_base_path="resnap")

    # When
    config = get_config_data(file_path)

    # Then
    assert isinstance(config, Config)
    assert config == expected
    mock_get_config_file_path.assert_not_called()


@pytest.mark.parametrize("file_path", ["", "test.txt"])
def test_should_return_default_config_data_with_warning(file_path: str, mock_get_config_file_path: MagicMock) -> None:
    # Given
    mock_get_config_file_path.return_value = file_path

    # When
    with patch.object(logging.getLogger("resnap"), "warning") as mock_warning:
        config = get_config_data()
        mock_warning.assert_called_once_with(f"Unsupported file type: {file_path}.")
        assert config == Config(enabled=True)


@pytest.mark.parametrize(
    "listdir_result, expected",
    [
        (["pyproject.toml"], "tests/pyproject.toml"),
        (["other_file.txt"], ""),
        (["another_file.txt", "pyproject.toml"], "tests/pyproject.toml"),
        ([], ""),
    ],
)
def test_should_get_config_file_path(listdir_result: list[str], expected: str, mock_os_listdir: MagicMock) -> None:
    # Given
    mock_os_listdir.return_value = listdir_result

    # When
    config_file_path = get_config_file_path()

    # Then
    assert Path(config_file_path) == Path(expected)
