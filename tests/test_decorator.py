import asyncio
import re
from datetime import datetime
from unittest.mock import MagicMock

import freezegun
import pytest

from resnap.decorators import async_resnap, resnap
from resnap.exceptions import ResnapError
from resnap.helpers.context import add_metadata
from resnap.helpers.metadata import Metadata
from resnap.helpers.utils import hash_arguments
from tests.builders.metadata_builder import MetadataFailBuilder, MetadataSuccessBuilder


@pytest.fixture(autouse=True)
def mock_service(mocker) -> None:
    mock: MagicMock = mocker.patch("resnap.decorators.ResnapServiceFactory.get_service", return_value=MagicMock())
    return mock


@resnap
def func(magic_number: int = 40) -> int:
    if magic_number < 0:
        raise ValueError("Magic number should be positive")
    if magic_number == 0:
        raise ResnapError("Magic number should not be null", data={"key": "value"})
    return magic_number + 2


@resnap(consider_args=False)
def func_not_consider_args(magic_number: int = 40) -> int:
    if magic_number < 0:
        raise ValueError("Magic number should be positive")
    if magic_number == 0:
        raise ResnapError("Magic number should not be null", data={"key": "value"})
    return magic_number + 2


@resnap(enable_recovery=False)
def func_disable_recovery(magic_number: int = 40) -> int:
    if magic_number < 0:
        raise ValueError("Magic number should be positive")
    if magic_number == 0:
        raise ResnapError("Magic number should not be null", data={"key": "value"})
    return magic_number + 2


@resnap(output_folder="toto")
def func_output_folder(magic_number: int = 40) -> int:
    if magic_number < 0:
        raise ValueError("Magic number should be positive")
    if magic_number == 0:
        raise ResnapError("Magic number should not be null", data={"key": "value"})
    return magic_number + 2


@async_resnap
async def async_func(magic_number: int = 40) -> int:
    await asyncio.sleep(0.1)
    if magic_number < 0:
        raise ValueError("Magic number should be positive")
    if magic_number == 0:
        raise ResnapError("Magic number should not be null", data={"key": "value"})
    return magic_number + 2


@resnap(output_format="str")
def func_str(magic_number: int = 40) -> int:
    return magic_number + 2


@resnap
def func_str_with_custom_metadata(magic_number: int = 40) -> int:
    add_metadata("key", "value")
    return magic_number + 2


@async_resnap
async def async_func_str_with_custom_metadata(magic_number: int = 40) -> int:
    add_metadata("key", "value")
    await asyncio.sleep(0.1)
    return magic_number + 2


@async_resnap(output_format="str")
async def async_func_str(magic_number: int = 40) -> int:
    await asyncio.sleep(0.1)
    return magic_number + 2


def test_should_not_use_service_if_disabled_sync(mock_service: MagicMock) -> None:
    # Given
    mock_service.return_value.is_enabled = False

    # When
    result = func()

    # Then
    assert result == 42
    mock_service.return_value.clear_old_saves.assert_not_called()


def test_should_return_result_if_metadata_exists_sync(mock_service: MagicMock) -> None:
    # Given
    mock_service.return_value.is_enabled = True
    mock_service.return_value.get_success_metadatas.return_value = [
        MetadataSuccessBuilder.a_metadata().with_arguments({"magic_number": 40}).build(),
        (
            MetadataSuccessBuilder.a_metadata()
            .with_event_time(datetime.fromisoformat("2021-01-02T00:00:00"))
            .with_arguments({"magic_number": 5})
            .build()
        ),
    ]
    mock_service.return_value.read_result.return_value = 42

    # When
    result = func()

    # Then
    assert result == 42
    mock_service.return_value.clear_old_saves.assert_called_once()
    mock_service.return_value.get_success_metadatas.assert_called_once()
    mock_service.return_value.read_result.assert_called_once()


@pytest.mark.parametrize(
    "metadata",
    [
        None,
        MetadataFailBuilder.a_metadata().build(),
        MetadataSuccessBuilder.a_metadata().with_arguments({"magic_number": 10}).build(),
    ],
)
def test_should_return_result_sync(metadata: Metadata | None, mock_service: MagicMock) -> None:
    # Given
    mock_service.return_value.is_enabled = True
    mock_service.return_value.get_success_metadatas.return_value = [metadata] if metadata else []
    now_time = datetime.now()
    mock_service.return_value.save_result.return_value = ("/path/to/result", now_time)

    # When
    result = func()

    # Then
    mock_service.return_value.read_result.assert_not_called()
    assert result == 42
    mock_service.return_value.clear_old_saves.assert_called_once()
    mock_service.return_value.get_success_metadatas.assert_called_once()
    mock_service.return_value.save_result.assert_called_with("func", 42, "", None)
    mock_service.return_value.save_success_metadata.assert_called_once_with(
        func_name="func",
        output_folder="",
        hashed_arguments=hash_arguments({"magic_number": 40}),
        event_time=now_time,
        result_path="/path/to/result",
        result_type=int.__name__,
        extra_metadata={},
    )


def test_should_use_output_format_option_sync(mock_service: MagicMock) -> None:
    # Given
    mock_service.return_value.is_enabled = True
    mock_service.return_value.get_success_metadatas.return_value = []
    now_time = datetime.now()
    mock_service.return_value.save_result.return_value = ("/path/to/result", now_time)

    # When
    result = func_str()

    # Then
    assert result == 42
    mock_service.return_value.save_result.assert_called_with("func_str", 42, "", "str")


def test_should_add_custom_metadata(mock_service: MagicMock) -> None:
    # Given
    mock_service.return_value.is_enabled = True
    mock_service.return_value.get_success_metadatas.return_value = []
    now_time = datetime.now()
    mock_service.return_value.save_result.return_value = ("/path/to/result", now_time)

    # When
    result = func_str_with_custom_metadata()

    # Then
    assert result == 42
    mock_service.return_value.save_result.assert_called_with("func_str_with_custom_metadata", 42, "", None)
    mock_service.return_value.save_success_metadata.assert_called_once_with(
        func_name="func_str_with_custom_metadata",
        output_folder="",
        hashed_arguments=hash_arguments({"magic_number": 40}),
        event_time=now_time,
        result_path="/path/to/result",
        result_type=int.__name__,
        extra_metadata={"key": "value"},
    )


def test_should_not_check_result_if_disabled(mock_service: MagicMock) -> None:
    # Given
    mock_service.return_value.is_enabled = True
    now_time = datetime.now()
    mock_service.return_value.save_result.return_value = ("/path/to/result", now_time)

    # When
    result = func_disable_recovery()

    # Then
    assert result == 42
    mock_service.return_value.read_result.assert_not_called()
    mock_service.return_value.save_result.assert_called_with("func_disable_recovery", 42, "", None)


def test_should_not_check_arguments_if_disabled(mock_service: MagicMock) -> None:
    # Given
    mock_service.return_value.is_enabled = True
    mock_service.return_value.read_result.return_value = 30
    metadata = MetadataSuccessBuilder.a_metadata().with_arguments({"magic_number": 30}).build()
    mock_service.return_value.get_success_metadatas.return_value = [metadata]

    # When
    result = func_not_consider_args(12)

    # Then
    assert result == 30
    mock_service.return_value.read_result.assert_called_once_with(metadata)
    mock_service.return_value.save_result.assert_not_called()


@freezegun.freeze_time("2021-01-01")
@pytest.mark.parametrize(
    "magic_number, error_type, error_message, expected_data",
    [
        (0, ResnapError, "Magic number should not be null", {"key": "value"}),
        (-1, ValueError, "Magic number should be positive", {}),
    ],
)
def test_should_raise_error_sync(
    magic_number: int,
    error_type: Exception,
    error_message: str,
    expected_data: dict,
    mock_service: MagicMock,
) -> None:
    # Given
    mock_service.return_value.is_enabled = True
    mock_service.return_value.get_success_metadatas.return_value = []

    # When
    with pytest.raises(error_type, match=re.escape(error_message)):
        func(magic_number)

    # Then
    mock_service.return_value.save_failed_metadata.assert_called_once_with(
        func_name="func",
        output_folder="",
        hashed_arguments=hash_arguments({"magic_number": magic_number}),
        event_time=datetime.fromisoformat("2021-01-01T00:00:00"),
        error_message=error_message,
        data=expected_data,
        extra_metadata={},
    )


def test_should_use_output_folder_sync(mock_service: MagicMock) -> None:
    # Given
    mock_service.return_value.is_enabled = True
    mock_service.return_value.get_success_metadatas.return_value = []
    now_time = datetime.now()
    mock_service.return_value.save_result.return_value = ("/path/to/result/toto", now_time)

    # When
    result = func_output_folder()

    # Then
    assert result == 42
    mock_service.return_value.save_result.assert_called_with("func_output_folder", 42, "toto", None)
    mock_service.return_value.save_success_metadata.assert_called_once_with(
        func_name="func_output_folder",
        output_folder="toto",
        hashed_arguments=hash_arguments({"magic_number": 40}),
        event_time=now_time,
        result_path="/path/to/result/toto",
        result_type=int.__name__,
        extra_metadata={},
    )


@pytest.mark.asyncio
async def test_should_add_custom_metadata_async(mock_service: MagicMock) -> None:
    # Given
    mock_service.return_value.is_enabled = True
    mock_service.return_value.get_success_metadatas.return_value = []
    now_time = datetime.now()
    mock_service.return_value.save_result.return_value = ("/path/to/result", now_time)

    # When
    result = await async_func_str_with_custom_metadata()

    # Then
    assert result == 42
    mock_service.return_value.save_result.assert_called_with("async_func_str_with_custom_metadata", 42, "", None)
    mock_service.return_value.save_success_metadata.assert_called_once_with(
        func_name="async_func_str_with_custom_metadata",
        output_folder="",
        hashed_arguments=hash_arguments({"magic_number": 40}),
        event_time=now_time,
        result_path="/path/to/result",
        result_type=int.__name__,
        extra_metadata={"key": "value"},
    )


@pytest.mark.asyncio
async def test_should_not_use_service_if_disabled_async(mock_service: MagicMock) -> None:
    # Given
    mock_service.return_value.is_enabled = False

    # When
    result = await async_func()

    # Then
    assert result == 42
    mock_service.return_value.clear_old_saves.assert_not_called()


@pytest.mark.asyncio
async def test_should_return_result_if_metadata_exists_async(mock_service: MagicMock) -> None:
    # Given
    mock_service.return_value.is_enabled = True
    mock_service.return_value.get_success_metadatas.return_value = [
        MetadataSuccessBuilder.a_metadata().with_arguments({"magic_number": 40}).build()
    ]
    mock_service.return_value.read_result.return_value = 42

    # When
    result = await async_func()

    # Then
    assert result == 42
    mock_service.return_value.clear_old_saves.assert_called_once()
    mock_service.return_value.get_success_metadatas.assert_called_once()
    mock_service.return_value.read_result.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "metadata",
    [
        None,
        MetadataFailBuilder.a_metadata().build(),
        MetadataSuccessBuilder.a_metadata().with_arguments({"magic_number": 10}).build(),
    ],
)
async def test_should_return_result_async(metadata: Metadata | None, mock_service: MagicMock) -> None:
    # Given
    mock_service.return_value.is_enabled = True
    mock_service.return_value.get_success_metadatas.return_value = [metadata] if metadata else []
    now_time = datetime.now()
    mock_service.return_value.save_result.return_value = ("/path/to/result", now_time)

    # When
    result = await async_func()

    # Then
    mock_service.return_value.read_result.assert_not_called()
    assert result == 42
    mock_service.return_value.clear_old_saves.assert_called_once()
    mock_service.return_value.get_success_metadatas.assert_called_once()
    mock_service.return_value.save_result.assert_called_with("async_func", 42, "", None)
    mock_service.return_value.save_success_metadata.assert_called_once_with(
        func_name="async_func",
        output_folder="",
        hashed_arguments=hash_arguments({"magic_number": 40}),
        event_time=now_time,
        result_path="/path/to/result",
        result_type=int.__name__,
        extra_metadata={},
    )


@pytest.mark.asyncio
async def test_should_use_output_format_option_async(mock_service: MagicMock) -> None:
    # Given
    mock_service.return_value.is_enabled = True
    mock_service.return_value.get_success_metadatas.return_value = []
    now_time = datetime.now()
    mock_service.return_value.save_result.return_value = ("/path/to/result", now_time)

    # When
    result = await async_func_str()

    # Then
    assert result == 42
    mock_service.return_value.save_result.assert_called_with("async_func_str", 42, "", "str")


@freezegun.freeze_time("2021-01-01", real_asyncio=True)
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "magic_number, error_type, error_message, expected_data",
    [
        (0, ResnapError, "Magic number should not be null", {"key": "value"}),
        (-1, ValueError, "Magic number should be positive", {}),
    ],
)
async def test_should_raise_error_async(
    magic_number: int,
    error_type: Exception,
    error_message: str,
    expected_data: dict,
    mock_service: MagicMock,
) -> None:
    # Given
    mock_service.return_value.is_enabled = True
    mock_service.return_value.get_success_metadatas.return_value = []

    # When
    with pytest.raises(error_type, match=re.escape(error_message)):
        await async_func(magic_number)

    # Then
    mock_service.return_value.save_failed_metadata.assert_called_once_with(
        func_name="async_func",
        output_folder="",
        hashed_arguments=hash_arguments({"magic_number": magic_number}),
        event_time=datetime.fromisoformat("2021-01-01T00:00:00"),
        error_message=error_message,
        data=expected_data,
        extra_metadata={},
    )
