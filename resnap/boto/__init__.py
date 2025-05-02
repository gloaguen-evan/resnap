import importlib.util

if importlib.util.find_spec("boto3") is None:
    raise ImportError("Please install the boto extra to save to S3: `pip install resnap[boto]`")

from .client import S3Client
from .config import S3Config

__all__ = [
    "S3Client",
    "S3Config",
]
