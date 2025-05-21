import io
import zlib
from abc import ABC, abstractmethod
from os import path

import pandas as pd
import pyarrow as pa

BufferType = io.FileIO | io.BytesIO | io.StringIO
_SUPPORTED_COMPRESSIONS = ["gzip"]
AVAILABLE_COMPRESSIONS = {"gzip": [".gz"], "snappy": ["*"]}


class DataFrameHandler(ABC):
    @staticmethod
    @abstractmethod
    def read_df(bytes_object, **kwargs) -> pd.DataFrame: ...  # pragma: no cover

    @staticmethod
    @abstractmethod
    def write_df(df: pd.DataFrame, remote_path: str, **kwargs) -> None: ...  # pragma: no cover

    @staticmethod
    def verify_compression_and_extension(compression: str | None, filepath: str) -> None:
        """Check compression mode.

        Args:
            compression (str | None): Compression mode.
            filepath (str): File path.

        Raises:
            ValueError: If compression is not supported or if the file extension does not match the compression mode.
        """
        if not compression:
            return
        if compression not in AVAILABLE_COMPRESSIONS:
            raise ValueError(
                f"{compression} not supported. It must be in this list: {', '.join(AVAILABLE_COMPRESSIONS)}"
            )
        else:
            _, extension = path.splitext(filepath)
            available_extensions = AVAILABLE_COMPRESSIONS[compression]
            if available_extensions != ["*"] and extension not in available_extensions:
                raise ValueError(
                    f"A {compression}-compressed file must have an extension in this "
                    f"list: {', '.join(available_extensions)}"
                )


class CSVHandler(DataFrameHandler):
    @staticmethod
    def read_df(
        bytes_object: BufferType,
        compression: str = "infer",
        nrows: int | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Read a CSV file from a bytes object and return it as a DataFrame.

        Args:
            bytes_object (BufferType): The bytes object containing the CSV data.
            compression (str): The compression method to use (e.g., "gzip").
            nrows (int | None): The number of rows to read from the CSV file. If None, read all rows.
            **kwargs: Additional arguments to pass to the pandas read_csv function.

        Returns:
            pd.DataFrame: The DataFrame containing the data from the CSV file.
        """
        if nrows is not None and compression == "gzip":  # top N from gzip file
            return CSVHandler._read_df_nrows_gzip(bytes_object, nrows=nrows, **kwargs)
        elif nrows is not None:  # top N from file
            return CSVHandler._read_df_nrows(bytes_object, nrows=nrows, compression=compression, **kwargs)
        return CSVHandler._read_df(bytes_object, compression, **kwargs)  # default behaviour

    @staticmethod
    def write_df(df: pd.DataFrame, compression: str | None = None, **kwargs) -> io.BytesIO:
        """Write a DataFrame to a bytes object in CSV format.

        Args:
            df (pd.DataFrame): The DataFrame to write.
            compression (str | None): The compression method to use (e.g., "gzip").
            **kwargs: Additional arguments to pass to the pandas to_csv function.

        Returns:
            io.BytesIO: The bytes object containing the CSV data.
        """
        if not compression:
            buffer = io.StringIO()
            df.to_csv(buffer, **kwargs)
            buffer = io.BytesIO(buffer.getvalue().encode())
            return buffer

        elif compression in _SUPPORTED_COMPRESSIONS:
            buffer = io.BytesIO()
            df.to_csv(buffer, compression=compression, **kwargs)  # Only works for pandas >=1.2.0
            buffer.seek(0)
            return buffer
        else:
            raise ValueError(f"{compression} compression not supported, supported one are: {_SUPPORTED_COMPRESSIONS}")

    @staticmethod
    def _read_df(bytes_object: BufferType, compression: str | None = None, **kwargs) -> pd.DataFrame:
        buffer = io.BytesIO(bytes_object.read())
        return pd.read_csv(buffer, compression=compression, **kwargs)

    @staticmethod
    def _read_df_nrows(bytes_object: BufferType, nrows: int, compression: str | None = None, **kwargs) -> pd.DataFrame:
        content = []
        for idx, line in enumerate(bytes_object.iter_lines()):
            if idx > nrows:
                break
            content.append(line)
        return pd.read_csv(io.BytesIO(b"\n".join(content)), compression=compression, nrows=nrows, **kwargs)

    @staticmethod
    def _read_df_nrows_gzip(bytes_object: BufferType, nrows: int, **kwargs) -> pd.DataFrame:
        content = b""
        decompressor = zlib.decompressobj(wbits=zlib.MAX_WBITS | 16)
        header = kwargs.get("header", 0)
        n_lines = 0
        for chunk in bytes_object.iter_chunks():
            decompressed_chunk = decompressor.decompress(chunk)
            n_lines += decompressed_chunk.count(b"\n")
            content += decompressed_chunk
            if n_lines - (header == 0) > nrows:
                break
        return pd.read_csv(io.BytesIO(content), compression=None, nrows=nrows, **kwargs)


class ParquetHandler(DataFrameHandler):
    @staticmethod
    def read_df(bytes_object: BufferType, **kwargs) -> pd.DataFrame:
        """Read a Parquet file from a bytes object and return it as a DataFrame.

        Args:
            bytes_object (BufferType): The bytes object containing the Parquet data.
            **kwargs: Additional arguments to pass to the pandas read_parquet function.

        Returns:
            pd.DataFrame: The DataFrame containing the data from the Parquet file.
        """
        kwargs.pop("engine", None)
        reader = pa.BufferReader(bytes_object.read())
        return pd.read_parquet(reader, engine="pyarrow", **kwargs)

    @staticmethod
    def write_df(df: pd.DataFrame, compression: str | None = None, **kwargs) -> io.BytesIO:
        """Write a DataFrame to a bytes object in Parquet format.

        Args:
            df (pd.DataFrame): The DataFrame to write.
            compression (str | None): The compression method to use (e.g., "gzip").
            **kwargs: Additional arguments to pass to the pandas to_parquet function.

        Returns:
            io.BytesIO: The bytes object containing the Parquet data.
        """
        kwargs.pop("engine", None)
        buffer = io.BytesIO()
        df.to_parquet(buffer, engine="pyarrow", compression=compression, **kwargs)
        buffer.seek(0)
        return buffer


HANDLERS_MAP = {
    "csv": CSVHandler,
    "parquet": ParquetHandler,
}


def get_dataframe_handler(file_format: str = "csv") -> DataFrameHandler:
    """Get the appropriate DataFrame handler based on the file format.

    Args:
        file_format (str): The file format (e.g., "csv", "parquet").

    Returns:
        DataFrameHandler: The appropriate DataFrame handler class.

    Raises:
        ValueError: If the file format is not supported.
    """
    if file_format not in HANDLERS_MAP.keys():
        raise ValueError(f"{file_format} is not supported. Valid ones are {', '.join(HANDLERS_MAP)}.")

    return HANDLERS_MAP[file_format]
