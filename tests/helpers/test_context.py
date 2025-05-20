import asyncio
import threading
from typing import Any

import pytest

from resnap.helpers.context import (
    add_metadata,
    add_metadatas,
    clear_metadata,
    get_metadata,
    restore_metadata,
)


def test_add_and_get_metadata() -> None:
    # Given
    clear_metadata()

    # When / Then
    add_metadata("key1", "value1")
    metadata = get_metadata()

    assert isinstance(metadata, dict)
    assert metadata == {"key1": "value1"}

    add_metadata("key2", 42)
    metadata = get_metadata()
    assert metadata == {"key1": "value1", "key2": 42}
    assert len(metadata) == 2

    # Finally
    clear_metadata()


def test_add_and_get_metadatas() -> None:
    # Given
    clear_metadata()

    # When / Then
    add_metadata("key1", "value0")
    metadatas = {
        "key1": "value1",
        "key2": 42,
        "key3": 3.14,
    }
    add_metadatas(metadatas)
    result = get_metadata()

    assert isinstance(result, dict)
    assert result == metadatas

    # Finally
    clear_metadata()


def test_clear_metadata() -> None:
    # Given
    add_metadata("key", "value")
    metadata = get_metadata()
    assert metadata == {"key": "value"}

    # When / Then
    clear_metadata()
    metadata = get_metadata()
    assert metadata == {}


def test_clear_and_restore_metadata():
    add_metadata("a", 1)
    assert get_metadata() == {"a": 1}

    token = clear_metadata()
    assert get_metadata() == {}

    add_metadata("b", 2)
    assert get_metadata() == {"b": 2}

    restore_metadata(token)
    assert get_metadata() == {"a": 1}


async def set_and_get_metadata_async(key, value) -> dict[str, Any]:
    clear_metadata()
    add_metadata(key, value)
    await asyncio.sleep(0.1)
    return get_metadata()


@pytest.mark.asyncio
async def test_async_metadata_isolation() -> None:
    result1, result2 = await asyncio.gather(
        set_and_get_metadata_async("a", 1), set_and_get_metadata_async("b", 2)
    )

    assert result1 == {"a": 1}
    assert result2 == {"b": 2}


def set_and_get_metadata_thread(key, value, result_holder, index) -> None:
    clear_metadata()
    add_metadata(key, value)
    result_holder[index] = get_metadata()


def test_thread_metadata_isolation() -> None:
    result_holder = [None, None]

    t1 = threading.Thread(
        target=set_and_get_metadata_thread, args=("x", "foo", result_holder, 0)
    )
    t2 = threading.Thread(
        target=set_and_get_metadata_thread, args=("y", "bar", result_holder, 1)
    )

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert result_holder[0] == {"x": "foo"}
    assert result_holder[1] == {"y": "bar"}
