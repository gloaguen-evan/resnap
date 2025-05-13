import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from ..helpers.constants import EXT
from ..helpers.metadata import Metadata
from ..helpers.status import Status
from ..helpers.utils import calculate_datetime_from_now, get_datetime_from_filename
from .service import ResnapService


class LocalResnapService(ResnapService):
    def clear_old_saves(self) -> None:
        limit_time: datetime = calculate_datetime_from_now(
            self.config.max_history_files_length, self.config.max_history_files_time_unit,
        )
        folders: set[Path] = set()
        for f in Path(self.config.output_base_path).rglob("*"):
            if f.is_dir():
                folders.add(f)
                continue
            if f.is_file() and EXT in f.name:
                file_time = get_datetime_from_filename(f.name)
                if file_time < limit_time:
                    f.unlink()
        for folder in folders:
            contents = list(folder.iterdir())
            if not contents:
                folder.rmdir()

    def _create_folder(self, path: str, folder_name: str) -> None:
        folder_path = Path(path) / folder_name
        folder_path.mkdir(exist_ok=True)

    @staticmethod
    def _read_metadata(metadata_path: Path) -> Metadata:
        with open(metadata_path, "r") as json_file:
            data = json.load(json_file)
        return Metadata.from_dict(data)

    def get_success_metadatas(self, func_name: str, output_folder: str) -> list[Metadata]:
        files: list[Path] = [
            Path(x) for x in Path(self._get_output_path(output_folder)).rglob(f"*{EXT}*")
            if x.is_file() and func_name in x.name and x.suffix == EXT
        ]

        if not files:
            return []

        metadatas: list[Metadata] = [self._read_metadata(f) for f in sorted(files, reverse=True)]
        return [m for m in metadatas if m.status == Status.SUCCESS]

    def _read_parquet_to_dataframe(self, file_path: str) -> pd.DataFrame:
        return pd.read_parquet(file_path)

    def _read_csv_to_dataframe(self, file_path: str) -> pd.DataFrame:
        return pd.read_csv(file_path, index_col=False)

    def _read_pickle(self, file_path: str) -> Any:
        with open(file_path, "rb") as f:
            return pickle.load(f)

    def _read_text(self, file_path: str) -> str:
        with open(file_path, "r") as f:
            return f.read()

    def _read_json(self, file_path: str) -> Any:
        with open(file_path, "r") as f:
            return json.load(f)

    @staticmethod
    def _save_dataframe_to_csv(result: pd.DataFrame, result_path: str) -> None:
        result.to_csv(result_path, index=False)

    @staticmethod
    def _save_dataframe_to_parquet(result: pd.DataFrame, result_path: str) -> None:
        result.to_parquet(result_path, compression="gzip")

    def _save_to_pickle(self, result: Any, result_path: str) -> None:
        with open(result_path, "wb") as f:
            pickle.dump(result, f)

    def _save_to_text(self, result: Any, result_path: str) -> None:
        with open(result_path, "w") as f:
            f.write(str(result))

    def _save_to_json(self, result: Any, result_path: str) -> None:
        with open(result_path, "w") as f:
            json.dump(result, f, indent=4)

    @staticmethod
    def _write_metadata(metadata_path: str, metadata: Metadata) -> None:
        with open(metadata_path, "w") as json_file:
            json.dump(metadata.to_dict(), json_file, indent=4)
