import hashlib
import json
from configparser import ConfigParser, SectionProxy
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any

import pandas as pd
import yaml


class Extensions(str, Enum):
    YML = ".yml"
    YAML = ".yaml"
    CFG = ".cfg"
    INI = ".ini"
    JSON = ".json"


def make_json_serializable(obj: Any) -> Any:
    """
    Convert an object to a JSON-serializable format.
    This function handles various types of objects, including pandas DataFrames,
    dataclasses, dictionaries, lists, tuples, sets, and primitive types.

    Args:
        obj (Any): The object to convert to a JSON-serializable format.
    Returns:
        Any: The JSON-serializable representation of the object.
    """
    match obj:
        case pd.DataFrame():
            # Sort DataFrame by index and columns to ensure stable output
            # and reset index to avoid issues with non-serializable index types
            df = obj.sort_index(axis=1).sort_index().reset_index(drop=True)
            return make_json_serializable(df.to_dict(orient="records"))  # Stable, JSON-compatible format

        case _ if is_dataclass(obj):
            return make_json_serializable(asdict(obj))

        case dict():
            return {str(k): make_json_serializable(v) for k, v in sorted(obj.items())}

        case list():
            return [make_json_serializable(v) for v in obj]

        case tuple():
            return tuple(make_json_serializable(v) for v in obj)

        case set():
            return sorted(make_json_serializable(v) for v in obj)

        case int() | float() | str() | bool() | None:
            return obj

        case _:
            try:
                return make_json_serializable(vars(obj))
            except TypeError:
                return str(obj)


def hash_arguments(args: dict[str, Any]) -> str:
    """
    Hash the given arguments to create a unique identifier.
    This function converts the arguments to a JSON-serializable format,
    serializes them to a JSON string, and then computes the SHA-256 hash.

    Args:
        args (dict[str, Any]): The arguments to hash.
    Returns:
        str: The SHA-256 hash of the JSON-serializable arguments.
    """
    serializable_args = make_json_serializable(args)
    json_string = json.dumps(serializable_args, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(json_string.encode("utf-8")).hexdigest()


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
