import logging
import os

import toml

from .helpers.config import Config

CONFIG_SECTIONS: dict[str, str] = {
    "pyproject.toml": "resnap",
}

logger = logging.getLogger("resnap")


def get_config_data(file_path: str | None = None) -> Config:
    """
    Get the configuration data from the specified file or the default file.
    If no file is specified, it will look for a default configuration file.

    Args:
        file_path (str | None): Path to the configuration file. If None, it will look for a default file.

    Returns:
        Config: Configuration data.
    """
    if not file_path:
        file_path = get_config_file_path()
    if file_path.endswith(".toml"):
        config = toml.load(file_path)
        tools = config.get("tool", {})
        settings = tools.get(CONFIG_SECTIONS["pyproject.toml"], {"enabled": True})
        return Config(**settings)
    else:
        logger.warning(f"Unsupported file type: {file_path}.")
        return Config(enabled=True)


def get_config_file_path() -> str:
    """
    Get the path to the configuration file.

    Returns:
        str: Path to the configuration file.
    """
    exec_path: str = os.getcwd()
    for file_name in CONFIG_SECTIONS:
        if file_name in os.listdir(exec_path):
            return os.path.join(exec_path, file_name)
    return ""
