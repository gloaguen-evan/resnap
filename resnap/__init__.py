"""Defines the public resnap interface"""

from .decorators import async_resnap, resnap
from .exceptions import ResnapError
from .factory import set_resnap_service
from .helpers.context import add_metadata, add_metadatas
from .services.service import ResnapService
from .version import VERSION

__version__ = VERSION
__all__ = (
    # decorators
    "resnap",
    "async_resnap",
    # exceptions
    "ResnapError",
    # factory
    "set_resnap_service",
    # metadatas
    "add_metadata",
    "add_metadatas",
    # services
    "ResnapService",
    # version
    "__version__",
    "VERSION",
)
