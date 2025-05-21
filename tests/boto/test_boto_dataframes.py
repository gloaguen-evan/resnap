import gzip
import io
import re
from unittest.mock import MagicMock

import pandas as pd
import pytest

from resnap.boto.dataframes import (
    _SUPPORTED_COMPRESSIONS,
    AVAILABLE_COMPRESSIONS,
    CSVHandler,
    DataFrameHandler,
    ParquetHandler,
    get_dataframe_handler,
)


@pytest.mark.parametrize(
    "file_format, expected_handler",
    [
        ("csv", CSVHandler),
        ("parquet", ParquetHandler),
    ],
)
def test_should_return_dataframe_handler(
    file_format: str, expected_handler: DataFrameHandler
) -> None:
    # When
    handler = get_dataframe_handler(file_format)

    # Then
    assert handler == expected_handler


def test_should_raise_value_error_for_invalid_file_format() -> None:
    # Given
    invalid_file_format = "invalid_format"

    # When / Then
    with pytest.raises(
        ValueError,
        match="invalid_format is not supported. Valid ones are csv, parquet.",
    ):
        get_dataframe_handler(invalid_file_format)


@pytest.fixture
def mock_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "col1": [1, 2],
            "col2": ["foo", "bar"],
        }
    )


class TestDataFrameHandler:
    @pytest.mark.parametrize(
        "compression, file_path",
        [
            (None, "test/dataframe.csv"),
            ("gzip", "test/dataframe.gz"),
            ("snappy", "test/dataframe.csv"),
        ],
    )
    def test_should_verify_compression_and_extension(
        self, compression: str | None, file_path: str
    ) -> None:
        # When
        DataFrameHandler.verify_compression_and_extension(compression, file_path)

        # Then
        assert True

    @pytest.mark.parametrize(
        "compression, file_path, expected_error_message",
        [
            pytest.param(
                "test",
                "test/dataframe.parquet",
                f"test not supported. It must be in this list: {', '.join(AVAILABLE_COMPRESSIONS)}",
                id="unsupported_compression",
            ),
            pytest.param(
                "gzip",
                "test/dataframe.csv",
                f"A gzip-compressed file must have an extension in this "
                f"list: {', '.join(AVAILABLE_COMPRESSIONS['gzip'])}",
                id="gzip_compression_invalid_extension",
            ),
        ],
    )
    def test_should_raise_value_error_for_invalid_compression_and_extension(
        self, compression: str, file_path: str, expected_error_message: str
    ) -> None:
        # When / Then
        with pytest.raises(ValueError, match=expected_error_message):
            DataFrameHandler.verify_compression_and_extension(compression, file_path)


class TestCSVHandler:
    def test_should_read_df(self, mock_dataframe: pd.DataFrame) -> None:
        # Given
        csv_content = b"col1,col2\n1,foo\n2,bar"
        fake_bytes_io = io.BytesIO(csv_content)

        # When
        result_df = CSVHandler.read_df(fake_bytes_io)

        # Then
        pd.testing.assert_frame_equal(result_df, mock_dataframe)

    def test_should_read_df_nrows(self, mock_dataframe: pd.DataFrame) -> None:
        # Given
        lines = [
            b"col1,col2",
            b"1,foo",
            b"2,bar",
            b"3,baz",
        ]
        mock_bytes_obj = MagicMock()
        mock_bytes_obj.iter_lines.return_value = iter(lines)

        # When
        result_df = CSVHandler.read_df(mock_bytes_obj, nrows=2)

        # Then
        pd.testing.assert_frame_equal(result_df, mock_dataframe)

    def test_should_read_df_nrows_gzip(self, mock_dataframe: pd.DataFrame) -> None:
        # Given
        csv_content = b"col1,col2\n1,foo\n2,bar\n3,baz\n4,qux\n"
        compressed_buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=compressed_buffer, mode="wb") as f:
            f.write(csv_content)
        compressed_bytes = compressed_buffer.getvalue()
        chunk_size = 10
        chunks = [
            compressed_bytes[i: i + chunk_size]
            for i in range(0, len(compressed_bytes), chunk_size)
        ]
        mock_bytes_obj = MagicMock()
        mock_bytes_obj.iter_chunks.return_value = iter(chunks)

        # When
        result_df = CSVHandler.read_df(mock_bytes_obj, compression="gzip", nrows=2)

        # Then
        pd.testing.assert_frame_equal(result_df, mock_dataframe)

    def test_should_write_df_with_no_compression(
        self, mock_dataframe: pd.DataFrame
    ) -> None:
        # When
        buffer = CSVHandler.write_df(mock_dataframe, index=False)

        # Then
        assert isinstance(buffer, io.BytesIO)
        buffer.seek(0)
        result_df = pd.read_csv(buffer)
        pd.testing.assert_frame_equal(result_df, mock_dataframe)

    def test_should_write_df_gzip_compression(
        self, mock_dataframe: pd.DataFrame
    ) -> None:
        # When
        buffer = CSVHandler.write_df(mock_dataframe, compression="gzip", index=False)

        # Then
        assert isinstance(buffer, io.BytesIO)
        buffer.seek(0)
        with gzip.GzipFile(fileobj=buffer, mode="rb") as f:
            decompressed = f.read()
        result_df = pd.read_csv(io.BytesIO(decompressed))
        pd.testing.assert_frame_equal(result_df, mock_dataframe)

    def test_should_raise_valueerror_when_write_df_with_invalid_compression(
        self, mock_dataframe: pd.DataFrame
    ) -> None:
        # When / Then
        with pytest.raises(
            ValueError,
            match=re.escape(
                f"test compression not supported, supported one are: {_SUPPORTED_COMPRESSIONS}"
            ),
        ):
            CSVHandler.write_df(mock_dataframe, compression="test")


class TestParquetHandler:
    def test_should_read_df(self, mock_dataframe: pd.DataFrame) -> None:
        # Given
        buffer = io.BytesIO()
        mock_dataframe.to_parquet(buffer, engine="pyarrow")
        buffer.seek(0)

        # When
        result_df = ParquetHandler.read_df(buffer)

        # Then
        pd.testing.assert_frame_equal(result_df, mock_dataframe)

    def test_should_write(self, mock_dataframe: pd.DataFrame) -> None:
        # When
        buffer = ParquetHandler.write_df(mock_dataframe)

        # Then
        assert isinstance(buffer, io.BytesIO)
        buffer.seek(0)
        result_df = pd.read_parquet(buffer, engine="pyarrow")
        pd.testing.assert_frame_equal(result_df, mock_dataframe)
