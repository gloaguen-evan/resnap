"""The `version` module holds the version information for resnap."""

__all__ = "VERSION"

VERSION = "0.1.1"
"""The version of resnap."""


def version_short() -> str:
    """Return the `major.minor` part of resnap version.

    It returns '1.2' if resnap version is '1.2.6'.
    """
    return ".".join(VERSION.split(".")[:2])
