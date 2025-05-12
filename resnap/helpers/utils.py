import hashlib
import io
import pickle
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

from .constants import EXT


class TimeUnit(str, Enum):
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"


def calculate_datetime_from_now(value: int, unit: TimeUnit) -> datetime:
    """
    Calculate datetime from now based on the given value and unit.

    Args:
        value (int): The value to calculate the datetime from now.
        unit (TimeUnit): The unit to calculate the datetime from now.
    Returns:
        datetime: The calculated datetime from now.
    """
    now = datetime.now()

    if unit == TimeUnit.SECOND:
        delta = timedelta(seconds=value)
    elif unit == TimeUnit.MINUTE:
        delta = timedelta(minutes=value)
    elif unit == TimeUnit.HOUR:
        delta = timedelta(hours=value)
    elif unit == TimeUnit.DAY:
        delta = timedelta(days=value)
    elif unit == TimeUnit.WEEK:
        delta = timedelta(weeks=value)
    else:  # pragma: no cover
        pass

    return now - delta


def get_datetime_from_filename(filename: Path | str) -> datetime:
    """
    Get datetime from the given filename.

    Args:
        filename (Path | str): The filename to get the datetime from.
    Returns:
        datetime: The datetime from the given filename.
    """
    filename_without_ext: str = str(filename).split(EXT)[0]
    return datetime.fromisoformat(filename_without_ext.split("_")[-1])


def hash_arguments(args: dict[str, Any]) -> str:
    """
    Hash the given arguments.

    Args:
        args (dict[str, Any]): The arguments to hash.
    Returns:
        str: The hashed arguments.
    """
    with io.BytesIO() as buffer:
        pickle.dump(args, buffer)
        serialized_args = buffer.getvalue()
    return hashlib.sha256(serialized_args).hexdigest()
