import io
import zlib
from abc import ABC, abstractmethod
from os import path

import pandas as pd

try:
    import pyarrow as pa
except ImportError:  # pragma: no cover
    pa = None

BufferType = io.FileIO | io.BytesIO | io.StringIO
_SUPPORTED_COMPRESSIONS = ["gzip"]
AVAILABLE_COMPRESSIONS = {"gzip": [".gz"], "snappy": ["*"]}


class DataFrameHandler(ABC):
    @staticmethod
    @abstractmethod
    def read_df(bytes_object, **kwargs) -> pd.DataFrame:  # pragma: no cover
        pass

    @staticmethod
    @abstractmethod
    def write_df(df: pd.DataFrame, remote_path: str, **kwargs) -> None:  # pragma: no cover
        pass

    @staticmethod
    def verify_compression_and_extension(compression: str | None, filepath: str) -> None:
        """check compression mode.

        :param compression: compression mode
        :raises ValueError: if unsupported compression mode
        :returns: None
        """
        if not compression:
            return
        if compression not in AVAILABLE_COMPRESSIONS:
            raise ValueError(
                "{} not supported. It must be in this list: {}".format(
                    compression, ", ".join([*AVAILABLE_COMPRESSIONS])
                )
            )
        else:
            _, extension = path.splitext(filepath)
            available_extensions = AVAILABLE_COMPRESSIONS[compression]
            if available_extensions != ["*"] and extension not in available_extensions:
                raise ValueError(
                    f"A {compression}-compressed file must have an extension in this "
                    "list: {', '.join(available_extensions)}"
                )


class CSVHandler(DataFrameHandler):
    @staticmethod
    def read_df(
        bytes_object: BufferType,
        compression: str = "infer",
        nrows: int | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        if nrows is not None and compression == "gzip":  # top N from gzip file
            return CSVHandler._read_df_nrows_gzip(bytes_object, nrows=nrows, **kwargs)
        elif nrows is not None:  # top N from file
            return CSVHandler._read_df_nrows(bytes_object, nrows=nrows, compresison=compression, **kwargs)
        return CSVHandler._read_df(bytes_object, compression, **kwargs)  # default behaviour

    @staticmethod
    def write_df(df: pd.DataFrame, compression: str | None = None, **kwargs) -> BufferType:
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
        kwargs.pop("engine", None)
        if not pa:
            raise ImportError("You need to install pyarrow to read parquet: `pip install pyarrow`")

        reader = pa.BufferReader(bytes_object)
        # compression is automatically handled by read_parquet function
        return pd.read_parquet(reader, engine="pyarrow", **kwargs)

    @staticmethod
    def write_df(df: pd.DataFrame, compression: str | None = None, **kwargs) -> BufferType:
        kwargs.pop("engine", None)
        if not pa:
            raise ImportError("You need to install pyarrow to write parquet: `pip install pyarrow`")

        buffer = io.BytesIO()
        df.to_parquet(buffer, engine="pyarrow", compression=compression, **kwargs)
        buffer.seek(0)
        return buffer


HANDLERS_MAP = {
    "csv": CSVHandler,
    "parquet": ParquetHandler,
}


def get_dataframe_handler(file_format: str = "csv") -> DataFrameHandler:
    if file_format not in HANDLERS_MAP.keys():
        raise ValueError("{} is not supported. Valid ones are {}.".format(file_format, ", ".join(HANDLERS_MAP.keys())))

    return HANDLERS_MAP[file_format]
