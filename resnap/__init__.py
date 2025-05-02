"""Defines the public resnap interface"""
from .decorators import resnap, async_resnap
from .exceptions import ResnapError
from .factory import set_resnap_service
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
    # services
    "ResnapService",
    # version
    "__version__",
    "VERSION",
)
