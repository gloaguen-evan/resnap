from contextvars import ContextVar, Token
from typing import Any

_resnap_metadata: ContextVar[dict] = ContextVar("_resnap_metadata", default={})


def add_metadata(key: str, value: Any) -> None:
    """
    Add metadata to the resnap context.

    Args:
        key (str): The key for the metadata.
        value (Any): The value for the metadata.
    """
    metadata = _resnap_metadata.get()
    metadata[key] = value
    _resnap_metadata.set(metadata)


def add_multiple_metadata(metadata: dict[str, Any]) -> None:
    """
    Add multiple metadata to the resnap context.

    Args:
        metadata (dict): The metadata to add.
    """
    current_metadata = _resnap_metadata.get()
    current_metadata.update(metadata)
    _resnap_metadata.set(current_metadata)


def get_metadata() -> dict:
    """
    Get the metadata from the resnap context.

    Returns:
        dict: The metadata from the resnap context.
    """
    return _resnap_metadata.get()


def clear_metadata() -> Token:
    """
    Clear the metadata from the resnap context.
    """
    return _resnap_metadata.set({})


def restore_metadata(token: Token) -> None:
    """
    Restore the metadata in the resnap context.

    Args:
        token (Token): The token to restore the metadata.
    """
    _resnap_metadata.reset(token)
