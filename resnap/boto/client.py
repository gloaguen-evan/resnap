import io
import json
from typing import Union

import pandas as pd
from botocore.exceptions import ClientError

from .config import S3Config
from .connection import get_s3_connection

SEPARATOR = "/"


def format_remote_path(path: str) -> str:
    return path.lstrip(SEPARATOR)


class S3Client:
    def __init__(self, config: S3Config) -> None:
        self.config = config
        self.bucket_name = config.bucket_name

    def upload_file(self, local_path_or_fileobj: Union[str, io.FileIO, io.BytesIO], remote_path: str) -> None:
        """Upload a file to S3.

        Args:
            local_path_or_fileobj (Union[str, io.FileIO, io.BytesIO]): Local file path or file-like object to upload.
            remote_path (str): S3 path (key) where the file will be uploaded.
        """
        remote_path = format_remote_path(remote_path)
        with get_s3_connection(self.config) as connection:
            if isinstance(local_path_or_fileobj, str):
                with open(local_path_or_fileobj, "rb") as file:
                    connection.upload_fileobj(file, self.bucket_name, remote_path)
            else:
                if isinstance(local_path_or_fileobj, io.BytesIO):
                    local_path_or_fileobj.seek(0)  # re-init the buffer read position
                connection.upload_fileobj(local_path_or_fileobj, self.bucket_name, remote_path)

    def download_file(self, local_path_or_fileobj: Union[str, io.FileIO, io.BytesIO], remote_path: str) -> None:
        """Download a file from S3.
        Args:
            local_path_or_fileobj (Union[str, io.FileIO, io.BytesIO]): Local file path or file-like object to download to.
            remote_path (str): S3 path (key) of the file to download.
        """
        remote_path = format_remote_path(remote_path)
        with get_s3_connection(self.config) as connection:
            if isinstance(local_path_or_fileobj, str):
                with open(local_path_or_fileobj, "wb") as file:
                    connection.download_file(self.bucket_name, remote_path, file)
            else:
                if isinstance(local_path_or_fileobj, io.BytesIO):
                    local_path_or_fileobj.seek(0)  # re-init the buffer read position
                connection.download_fileobj(self.bucket_name, remote_path, local_path_or_fileobj)

    def list_objects(self, prefix: str = "", recursive: bool = False) -> list[str]:
        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        contents = response.get("Contents", [])
        return [obj["Key"] for obj in contents]

    def delete_object(self, key: str):
        self.s3.delete_object(Bucket=self.bucket_name, Key=key)

    def delete_objects(self, keys: list[str]):
        objects = [{"Key": key} for key in keys]
        if objects:
            self.s3.delete_objects(Bucket=self.bucket_name, Delete={"Objects": objects})

    def object_exists(self, key: str) -> bool:
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    def mkdir(self, path: str) -> None:
        """Create a directory in S3. In S3, directories are represented by keys that end with a '/'.

        Args:
            path (str): The path to create.
        """
        if not path.endswith(SEPARATOR):
            path += SEPARATOR
        self.upload_file(io.BytesIO(), path)

    def get_df_from_file(self, file_path: str, file_format: str) -> Union[pd.DataFrame, None]:
        """Read a file from S3 and return it as a DataFrame.

        Args:
            file_path (str): The S3 path to the file.
            file_format (str): The format of the file (e.g., "csv", "parquet").

        Returns:
            pd.DataFrame: The DataFrame containing the data from the file.
        """
        if file_format == "csv":
            return pd.read_csv(file_path)
        elif file_format == "parquet":
            return pd.read_parquet(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    def push_df_to_file(self, df: pd.DataFrame, file_path: str, file_format: str) -> None:
        """Save a DataFrame to a file in S3.

        Args:
            df (pd.DataFrame): The DataFrame to save.
            file_path (str): The S3 path where the file will be saved.
            file_format (str): The format of the file (e.g., "csv", "parquet").
        """
        if file_format == "csv":
            df.to_csv(file_path, index=False)
        elif file_format == "parquet":
            df.to_parquet(file_path, index=False)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    def push_to_file(self, data: Union[dict, str], file_path: str, file_format: str) -> None:
        """Save data to a file in S3.

        Args:
            data (Union[dict, str]): The data to save.
            file_path (str): The S3 path where the file will be saved.
            file_format (str): The format of the file (e.g., "json", "text").
        """
        if file_format == "json":
            self.upload_file(io.BytesIO(json.dumps(data).encode()), file_path)
        elif file_format == "text":
            self.upload_file(io.BytesIO(data.encode()), file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
