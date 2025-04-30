import io
import json
import pickle
from datetime import datetime
from typing import Any

import pandas as pd

from ..boto import (
    get_s3_connection,
    list_dir_in_bucket,
    exists_in_bucket,
    is_s3_dir,
    mkdir_in_bucket,
    download_file,
    delete_in_bucket,
    push_df_to_file,
    push_to_file,
    get_df_from_file,
    rmdir_in_bucket,
)
from ..helpers.constants import SEPATOR, EXT
from ..helpers.metadata import Metadata
from ..helpers.status import Status
from ..helpers.utils import calculate_datetime_from_now, get_datetime_from_filename
from .service import ResnapService


class BotoResnapService(ResnapService):
    @staticmethod
    def _format_path(path: str) -> str:
        return path if path.endswith(SEPATOR) else f"{path}{SEPATOR}"

    def clear_old_saves(self) -> None:
        limit_time: datetime = calculate_datetime_from_now(
            self.config.max_history_files_length, self.config.max_history_files_time_unit
        )
        with get_s3_connection(**self.secrets) as con:
            if not exists_in_bucket(self._format_path(self.config.output_base_path), con):
                return
            contents = list_dir_in_bucket(self.config.output_base_path, con, True)
            folders: set = set()
            for content in contents:
                if is_s3_dir(content, con):
                    folders.add(content)
                    continue
                if EXT not in content:
                    continue
                file_time = get_datetime_from_filename(content)
                if file_time < limit_time:
                    delete_in_bucket(content, con)
            for folder in folders:
                contents = list_dir_in_bucket(folder, con)
                if not contents:
                    rmdir_in_bucket(folder, con)

    def _create_folder(self, path: str, folder_name: str) -> None:
        with get_s3_connection(**self.secrets) as con:
            if path and not exists_in_bucket(self._format_path(path), con):
                mkdir_in_bucket(path, con)
            if folder_name:
                output_path = SEPATOR.join([path, folder_name])
                if not exists_in_bucket(self._format_path(output_path), con):
                    mkdir_in_bucket(output_path, con)

    def _read_metadata(self, metadata_path: str) -> Metadata:
        with self._get_buffer_for_read_file(metadata_path) as buffer:
            data = json.load(buffer)

        return Metadata.from_dict(data)

    def get_success_metadatas(self, func_name: str, output_folder: str) -> list[Metadata]:
        with get_s3_connection(**self.secrets) as con:
            files: list[str] = [
                file for file in list_dir_in_bucket(self._get_output_path(output_folder), con)
                if func_name in file and file.endswith(EXT)
            ]

        if not files:
            return []

        metadatas: list[Metadata] = [self._read_metadata(f) for f in sorted(files, reverse=True)]
        return [m for m in metadatas if m.status == Status.SUCCESS]

    def _read_parquet_to_dataframe(self, file_path: str) -> pd.DataFrame:
        with get_s3_connection(**self.secrets) as con:
            return get_df_from_file(file_path, con, file_format="parquet")

    def _read_csv_to_dataframe(self, file_path: str) -> pd.DataFrame:
        with get_s3_connection(**self.secrets) as con:
            return get_df_from_file(file_path, con, file_format="csv")

    def _get_buffer_for_read_file(self, file_path: str) -> io.BytesIO:
        buffer = io.BytesIO()

        with get_s3_connection(**self.secrets) as con:
            download_file(file_path, buffer, con)
        buffer.seek(0)
        return buffer

    def _read_pickle(self, file_path: str) -> Any:
        with self._get_buffer_for_read_file(file_path) as buffer:
            return pickle.loads(buffer.read())

    def _read_text(self, file_path: str) -> str:
        with self._get_buffer_for_read_file(file_path) as buffer:
            return buffer.read().decode()

    def _read_json(self, file_path: str) -> Any:
        with self._get_buffer_for_read_file(file_path) as buffer:
            return json.load(buffer)

    def _save_dataframe_to_csv(self, result: pd.DataFrame, result_path: str) -> None:
        with get_s3_connection(**self.secrets) as con:
            push_df_to_file(result, result_path, con, file_format="csv")

    def _save_dataframe_to_parquet(self, result: pd.DataFrame, result_path: str) -> None:
        with get_s3_connection(**self.secrets) as con:
            push_df_to_file(result, result_path, con, compression="gzip", file_format="parquet")

    def _save_buffer(self, buffer: io.BytesIO, result_path: str) -> None:
        buffer.seek(0)
        with get_s3_connection(**self.secrets) as con:
            push_to_file(buffer, result_path, con)

    def _save_to_pickle(self, result: Any, result_path: str) -> None:
        with io.BytesIO() as buffer:
            pickle.dump(result, buffer)
            self._save_buffer(buffer, result_path)

    def _save_to_text(self, result: Any, result_path: str) -> None:
        with io.BytesIO() as buffer:
            buffer.write(str(result).encode())
            self._save_buffer(buffer, result_path)

    def _save_to_json(self, result: Any, result_path: str) -> None:
        with io.BytesIO() as buffer:
            buffer.write(json.dumps(result, indent=4).encode())
            self._save_buffer(buffer, result_path)

    def _write_metadata(self, metadata_path: str, metadata: Metadata) -> None:
        with io.BytesIO() as buffer:
            buffer.write(json.dumps(metadata.to_dict(), indent=4).encode())
            self._save_buffer(buffer, metadata_path)
