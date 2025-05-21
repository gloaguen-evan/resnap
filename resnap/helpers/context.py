from contextvars import ContextVar, Token
from typing import Any

_checkpoint_metadata: ContextVar[dict] = ContextVar("_checkpoint_metadata", default={})


def add_metadata(key: str, value: Any) -> None:
    """
    Add metadata to the checkpoint context.

    Args:
        key (str): The key for the metadata.
        value (Any): The value for the metadata.
    """
    metadata = _checkpoint_metadata.get()
    metadata[key] = value
    _checkpoint_metadata.set(metadata)


def add_metadatas(metadata: dict[str, Any]) -> None:
    """
    Add multiple metadata to the checkpoint context.

    Args:
        metadata (dict): The metadata to add.
    """
    current_metadata = _checkpoint_metadata.get()
    current_metadata.update(metadata)
    _checkpoint_metadata.set(current_metadata)


def get_metadata() -> dict:
    """
    Get the metadata from the checkpoint context.

    Returns:
        dict: The metadata from the checkpoint context.
    """
    return _checkpoint_metadata.get()


def clear_metadata() -> None:
    """
    Clear the metadata from the checkpoint context.
    """
    return _checkpoint_metadata.set({})


def restore_metadata(token: Token) -> None:
    """
    Restore the metadata in the checkpoint context.

    Args:
        token (Token): The token to restore the metadata.
    """
    _checkpoint_metadata.reset(token)
