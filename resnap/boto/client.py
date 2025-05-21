import io

import pandas as pd

from .config import S3Config
from .connection import get_s3_connection
from .dataframes import get_dataframe_handler
from .tools import SEPARATOR, format_remote_path_folder_to_search, get_folders_and_files, remove_separator_at_begin

_UNDEFINED_VALUE = object()


class S3Client:
    """S3Client is a class that provides methods to interact with Amazon S3 or Ceph.
    It allows uploading, downloading, listing, and deleting files and directories in S3.

    Attributes:
        config (S3Config): Configuration object containing S3 connection details.
    """

    def __init__(self, config: S3Config) -> None:
        self.config = config
        self.bucket_name = config.bucket_name

    def upload_file(self, local_path_or_fileobj: str | io.FileIO | io.BytesIO, remote_path: str) -> None:
        """Upload a file to S3.

        Args:
            local_path_or_fileobj (str | io.FileIO | io.BytesIO): Local file path or file-like object to upload.
            remote_path (str): S3 path (key) where the file will be uploaded.
        """
        remote_path = remove_separator_at_begin(remote_path)
        with get_s3_connection(self.config) as connection:
            if isinstance(local_path_or_fileobj, str):
                with open(local_path_or_fileobj, "rb") as file:
                    connection.upload_fileobj(file, self.bucket_name, remote_path)
            else:
                if isinstance(local_path_or_fileobj, io.BytesIO):
                    local_path_or_fileobj.seek(0)  # re-init the buffer read position
                connection.upload_fileobj(local_path_or_fileobj, self.bucket_name, remote_path)

    def download_file(self, local_path_or_fileobj: str | io.FileIO | io.BytesIO, remote_path: str) -> None:
        """Download a file from S3.

        Args:
            local_path_or_fileobj (str | io.FileIO | io.BytesIO): Local file path or file-like object to download to.
            remote_path (str): S3 path (key) of the file to download.
        """
        remote_path = remove_separator_at_begin(remote_path)
        with get_s3_connection(self.config) as connection:
            if isinstance(local_path_or_fileobj, str):
                with open(local_path_or_fileobj, "wb") as file:
                    connection.download_fileobj(self.bucket_name, remote_path, file)
            else:
                if isinstance(local_path_or_fileobj, io.BytesIO):
                    local_path_or_fileobj.seek(0)  # re-init the buffer read position
                connection.download_fileobj(self.bucket_name, remote_path, local_path_or_fileobj)

    def list_objects(self, remote_dir_path: str = "", recursive: bool = False) -> list[str]:
        """List objects in a directory in S3.
        Args:
            remote_dir_path (str): The S3 path to the directory.
            recursive (bool): Whether to list objects recursively.

        Returns:
            List[str]: A list of object keys in the specified directory.
        """
        folders, files = self.list_folders_and_files(remote_dir_path, recursive)
        return sorted(folders + files)

    def list_folders_and_files(self, remote_dir_path: str = "", recursive: bool = False) -> tuple[list[str], list[str]]:
        """List folders and files in a directory in S3.

        Args:
            remote_dir_path (str): The S3 path to the directory.
            recursive (bool): Whether to list objects recursively.

        Returns:
            tuple[list[str], list[str]]: A tuple containing two lists: folders and files.
        """
        remote_dir_path = format_remote_path_folder_to_search(remote_dir_path)
        prefix = remote_dir_path[: remote_dir_path.index("*")]
        operation_parameters = {
            "Bucket": self.bucket_name,
            "Prefix": prefix,
        }
        if not recursive:
            operation_parameters["Delimiter"] = SEPARATOR

        with get_s3_connection(self.config) as connection:
            paginator = connection.get_paginator("list_objects_v2")
            page_iterator = paginator.paginate(**operation_parameters)
            folders, files = get_folders_and_files(remote_dir_path, page_iterator)
            return folders, files

    def delete_object(self, key: str) -> None:
        """Delete an object from S3.

        Args:
            key (str): The S3 key of the object to delete.
        """
        with get_s3_connection(self.config) as connection:
            connection.delete_object(Bucket=self.bucket_name, Key=key)

    def delete_objects(self, keys: list[str]) -> None:
        """Delete multiple objects from S3.

        Args:
            keys (list[str]): A list of S3 keys of the objects to delete.
        """
        objects = [{"Key": key} for key in keys]
        if not objects:
            return
        with get_s3_connection(self.config) as connection:
            connection.delete_objects(Bucket=self.bucket_name, Delete={"Objects": objects})

    def object_exists(self, remote_path: str) -> bool:
        """Check if an object exists in S3.

        Args:
            remote_path (str): The S3 path (key) of the object to check.

        Returns:
            bool: True if the object exists, False otherwise.
        """
        remote_path = remove_separator_at_begin(remote_path)
        with get_s3_connection(self.config) as connection:
            try:
                if remote_path == SEPARATOR:
                    connection.get_bucket_acl(Bucket=self.bucket_name)
                elif remote_path.endswith(SEPARATOR):
                    connection.get_object(Bucket=self.bucket_name, Key=remote_path)
                else:
                    connection.head_object(Bucket=self.bucket_name, Key=remote_path)
                return True
            except Exception:
                return False

    def mkdir(self, path: str) -> None:
        """Create a directory in S3. In S3, directories are represented by keys that end with a '/'.

        Args:
            path (str): The path to create.
        """
        if not path.endswith(SEPARATOR):
            path += SEPARATOR
        self.upload_file(io.BytesIO(), path)

    def rmdir(self, path: str) -> None:
        """Remove a directory in S3. In S3, directories are represented by keys that end with a '/'.

        Args:
            path (str): The path to remove.
        """
        path = format_remote_path_folder_to_search(path)
        folders, files = self.list_folders_and_files(path, recursive=True)
        self.delete_objects(files)
        self.delete_objects(folders)

    def get_df_from_file(self, remote_path: str, file_format: str = "csv", **kwargs) -> pd.DataFrame | None:
        """Read a file from S3 and return it as a DataFrame.

        Args:
            remote_path (str): The S3 path to the file.
            file_format (str): The format of the file (e.g., "csv", "parquet").

        Returns:
            pd.DataFrame: The DataFrame containing the data from the file.
        """
        df_handler = get_dataframe_handler(file_format)
        df_handler.verify_compression_and_extension(kwargs.get("compression"), remote_path)

        remote_path = remove_separator_at_begin(remote_path)
        if not self.object_exists(remote_path):
            raise FileNotFoundError(f"File {remote_path} not exists in bucket {self.bucket_name}")

        with get_s3_connection(self.config) as connection:
            bytes_object = connection.get_object(Bucket=self.bucket_name, Key=remote_path)["Body"]
            return df_handler.read_df(bytes_object, **kwargs)

    def push_df_to_file(
        self,
        df: pd.DataFrame,
        remote_path: str,
        compression: str | None = _UNDEFINED_VALUE,
        file_format: str = "csv",
        **kwargs,
    ) -> None:
        """Save a DataFrame to a file in S3.

        Args:
            df (pd.DataFrame): The DataFrame to save.
            remote_path (str): The S3 path where the file will be saved.
            compression (str | None): The compression method to use (e.g., "gzip").
            file_format (str): The format of the file (e.g., "csv", "parquet").
        """
        if compression is _UNDEFINED_VALUE:
            compression = "snappy" if file_format == "parquet" else None

        df_handler = get_dataframe_handler(file_format)
        df_handler.verify_compression_and_extension(compression, remote_path)

        remote_path = remove_separator_at_begin(remote_path)
        bytes_object = df_handler.write_df(df, compression=compression, **kwargs)
        self.upload_file(bytes_object, remote_path)
