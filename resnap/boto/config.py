from typing import Optional

from pydantic import BaseModel


class S3Config(BaseModel):
    access_key: str
    secret_key: str
    bucket_name: str
    region_name: Optional[str] = None
    endpoint_url: Optional[str] = None
    force_path_style: bool = True
    signature_version: str = "s3v4"
