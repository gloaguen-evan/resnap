import io
import json
import pickle
from datetime import datetime
from typing import Any

import pandas as pd

from ..boto import S3Client, S3Config
from ..helpers.config import Config
from ..helpers.constants import EXT, SEPATOR
from ..helpers.metadata import Metadata
from ..helpers.status import Status
from ..helpers.utils import calculate_datetime_from_now, get_datetime_from_filename, load_file
from .service import ResnapService


class BotoResnapService(ResnapService):
    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self._client: S3Client = S3Client(
            S3Config(**load_file(config.secrets_file_name, key="resnap"))
        )

    @staticmethod
    def _format_path(path: str) -> str:
        return path if path.endswith(SEPATOR) else f"{path}{SEPATOR}"

    def clear_old_saves(self) -> None:
        if not self._client.object_exists(self._format_path(self.config.output_base_path)):
            return

        contents = self._client.list_objects(self.config.output_base_path, True)
        empty_folders: list[str] = self._clear_files(contents)
        if empty_folders:
            self._clear_folders(empty_folders)

    def _clear_files(self, files: list[str]) -> list[str]:
        limit_time: datetime = calculate_datetime_from_now(
            self.config.max_history_files_length, self.config.max_history_files_time_unit,
        )

        folders: set = set()
        to_delete: list = []
        for file in files:
            if file.endswith(SEPATOR):
                folders.add(file)
                continue
            if EXT not in file:
                continue
            file_time = get_datetime_from_filename(file)
            if file_time < limit_time:
                to_delete.append(file)

        if to_delete:
            self._client.delete_objects(to_delete)
        return folders

    def _clear_folders(self, folders: set[str]) -> None:
        to_delete = []
        for folder in folders:
            contents = self._client.list_objects(folder)
            if not contents or (len(contents) == 1 and contents[0] == folder):
                to_delete.append(folder)
        if to_delete:
            self._client.delete_objects(to_delete)

    def _create_folder(self, path: str, folder_name: str) -> None:
        if path and not self._client.object_exists(self._format_path(path)):
            self._client.mkdir(path)
        if folder_name:
            output_path = SEPATOR.join([path, folder_name])
            if not self._client.object_exists(self._format_path(output_path)):
                self._client.mkdir(output_path)

    def _read_metadata(self, metadata_path: str) -> Metadata:
        with self._get_buffer_for_read_file(metadata_path) as buffer:
            data = json.load(buffer)

        return Metadata.from_dict(data)

    def get_success_metadatas(self, func_name: str, output_folder: str) -> list[Metadata]:
        files: list[str] = [
            file for file in self._client.list_objects(self._get_output_path(output_folder))
            if func_name in file and file.endswith(EXT)
        ]

        if not files:
            return []

        metadatas: list[Metadata] = [self._read_metadata(f) for f in sorted(files, reverse=True)]
        return [m for m in metadatas if m.status == Status.SUCCESS]

    def _read_parquet_to_dataframe(self, file_path: str) -> pd.DataFrame:
        return self._client.get_df_from_file(file_path, file_format="parquet")

    def _read_csv_to_dataframe(self, file_path: str) -> pd.DataFrame:
        return self._client.get_df_from_file(file_path, file_format="csv")

    def _get_buffer_for_read_file(self, file_path: str) -> io.BytesIO:
        buffer = io.BytesIO()
        self._client.download_file(buffer, file_path)
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
        self._client.push_df_to_file(result, result_path, file_format="csv")

    def _save_dataframe_to_parquet(self, result: pd.DataFrame, result_path: str) -> None:
        self._client.push_df_to_file(result, result_path, compression="gzip", file_format="parquet")

    def _save_to_pickle(self, result: Any, result_path: str) -> None:
        with io.BytesIO() as buffer:
            pickle.dump(result, buffer)
            self._client.upload_file(buffer, result_path)

    def _save_to_text(self, result: Any, result_path: str) -> None:
        with io.BytesIO() as buffer:
            buffer.write(str(result).encode())
            self._client.upload_file(buffer, result_path)

    def _save_to_json(self, result: Any, result_path: str) -> None:
        with io.BytesIO() as buffer:
            buffer.write(json.dumps(result, indent=4).encode())
            self._client.upload_file(buffer, result_path)

    def _write_metadata(self, metadata_path: str, metadata: Metadata) -> None:
        with io.BytesIO() as buffer:
            buffer.write(json.dumps(metadata.to_dict(), indent=4).encode())
            self._client.upload_file(buffer, metadata_path)
