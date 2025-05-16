from pydantic import BaseModel


class S3Config(BaseModel):
    access_key: str
    secret_key: str
    bucket_name: str
    region_name: str | None = None
    endpoint_url: str | None = None
    force_path_style: bool = True
    signature_version: str = "s3v4"
    cert_file_path: str | None = None
