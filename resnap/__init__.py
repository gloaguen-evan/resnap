"""Defines the public resnap interface"""

from .decorators import async_resnap, resnap
from .exceptions import ResnapError
from .factory import set_resnap_service
from .helpers.config import Config, Services
from .helpers.context import add_metadata, add_multiple_metadata
from .services.service import ResnapService
from .version import VERSION

__version__ = VERSION
__all__ = (
    # configuration
    "Config",
    "Services",
    # decorators
    "resnap",
    "async_resnap",
    # exceptions
    "ResnapError",
    # factory
    "set_resnap_service",
    # metadata
    "add_metadata",
    "add_multiple_metadata",
    # services
    "ResnapService",
    # version
    "__version__",
    "VERSION",
)
