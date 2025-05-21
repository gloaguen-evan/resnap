import hashlib
import io
import json
import pickle
from configparser import ConfigParser, SectionProxy
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

from .constants import EXT


class Extensions(str, Enum):
    YML = ".yml"
    YAML = ".yaml"
    CFG = ".cfg"
    INI = ".ini"
    JSON = ".json"


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
    extract_day, extract_time = filename_without_ext.split("_")[-1].split("T")
    extract_time = extract_time.replace("-", ":")
    return datetime.fromisoformat(f"{extract_day}T{extract_time}")


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


def load_file(file_path: str, key: str | None = None) -> dict | ConfigParser | SectionProxy:
    """
    Load a file into a dictionary or ConfigParser object.

    Args:
        file_path (str): The path to the file.
        key (str | None): The key to retrieve from the file. Defaults to None.

    Returns:
        dict | ConfigParser: The loaded file data.

    Raises:
        ValueError: If the file format is not supported.
        KeyError: If the key is not found in the file.
    """
    if file_path.endswith(Extensions.YML) or file_path.endswith(Extensions.YAML):
        file_dict = _load_yaml_file(file_path=file_path)
    elif file_path.endswith(Extensions.CFG) or file_path.endswith(Extensions.INI):
        file_dict = _load_cfg_file(file_path=file_path)
    elif file_path.endswith(Extensions.JSON):
        file_dict = _load_json_file(file_path=file_path)
    else:
        raise ValueError("File format not supported")

    try:
        return file_dict[key] if key else file_dict
    except KeyError:
        raise KeyError(f"Key {key} not found in {file_path}")


def _load_yaml_file(file_path: str) -> dict:
    """
    Load a yaml file into a dictionary

    Args:
        file_path (str): Path to the file

    Returns:
        dict: yaml file data
    """
    with open(file_path, "r") as stream:
        return yaml.safe_load(stream) or {}


def _load_cfg_file(file_path: str) -> ConfigParser:
    """
    Load a cfg file into a ConfigParser object

    Args:
        file_path (str): Path to the file

    Returns:
        ConfigParser: cfg file data
    """
    config_parser = ConfigParser(
        interpolation=None, converters={"list": json.loads, "dict": json.loads}
    )
    config_parser.read(file_path)
    return config_parser


def _load_json_file(file_path: str) -> dict:
    """
    Load a json file into a dictionary

    Args:
        file_path (str): Path to the file

    Returns:
        dict: json file data
    """
    with open(file_path, "r") as f:
        return json.load(f)
