import os
import toml
import logging
from .helpers.config import Config

CONFIG_SECTIONS: dict[str, str] = {
    "pyproject.toml": "resnap",
}

logger = logging.getLogger("resnap")


def get_config_data() -> Config:
    file_path = get_config_file_path()
    if file_path.endswith(".toml"):
        config = toml.load(file_path)
        tools = config.get("tool", {})
        settings = tools.get(CONFIG_SECTIONS["pyproject.toml"], Config(enabled=True))
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
    for file_name in CONFIG_SECTIONS:
        if file_name in os.listdir(os.getcwd()):
            return os.path.join(os.getcwd(), file_name)
    return ""
