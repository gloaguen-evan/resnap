from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import pandas as pd

from ..helpers.config import Config
from ..helpers.constants import EXT, SEPATOR
from ..helpers.metadata import Metadata, MetadataFail, MetadataSuccess
from ..helpers.singleton import SingletonABCMeta
from ..helpers.status import Status


class ResnapService(ABC, metaclass=SingletonABCMeta):
    def __init__(self, config: Config) -> None:
        self.config: Config = config

    @property
    def is_enabled(self) -> bool:
        return self.config.enabled

    def metadata_path(self, func_name: str, event_time: datetime, output_folder: str) -> str:
        """
        Get the metadata path based on the function name and event time.

        Args:
            func_name (str): The function name.
            event_time (datetime): The event time.
            output_folder (str): The output folder.
        Returns:
            str: The metadata path.
        """
        parts = []
        if self.config.output_base_path:
            parts.append(self.config.output_base_path)
        if output_folder:
            parts.append(output_folder)
        parts.append(f"{func_name}_{event_time.isoformat().replace(':', '-')}{EXT}")
        return SEPATOR.join(parts)

    def result_path(self, func_name: str, event_time: datetime, output_folder: str, output_ext: str) -> str:
        """
        Get the result path based on the function name, event time, and output extension.

        Args:
            func_name (str): The function name.
            event_time (datetime): The event time.
            output_folder (str): The output folder.
            output_ext (str): The output extension.
        Returns:
            str: The result path.
        """
        parts = []
        if self.config.output_base_path:
            parts.append(self.config.output_base_path)
        if output_folder:
            parts.append(output_folder)
        parts.append(f"{func_name}_{event_time.isoformat().replace(':', '-')}{EXT}.{output_ext}")
        return SEPATOR.join(parts)

    @abstractmethod
    def clear_old_saves(self) -> None:  # pragma: no cover
        """
        Clear old saves (metadata and saved files) based on the configuration.
        """
        raise NotImplementedError

    def _get_output_path(self, output_folder: str) -> str:
        output_path = self.config.output_base_path
        if output_folder:
            output_path += f"/{output_folder}"
        return output_path

    @abstractmethod
    def _create_folder(self, path: str, folder_name: str) -> None:  # pragma: no cover
        """
        Create the output folder based on the configuration.
        Args:
            path (str): The path to create the folder.
            folder_name (str): The name of the folder.
        """
        raise NotImplementedError

    def create_output_folder(self, output_folder: str) -> None:
        """
        Create the output folder based on the configuration.

        Args:
            output_folder (str): The output folder.
        """
        if self.config.output_base_path:
            self._create_folder("", self.config.output_base_path)
        if output_folder:
            self._create_folder(self.config.output_base_path, output_folder)

    @abstractmethod
    def get_success_metadatas(self, func_name: str, output_folder: str) -> list[Metadata]:  # pragma: no cover
        """
        Get all success metadatas based on the function name.

        Args:
            func_name (str): The function name.
            output_folder (str): The output folder.
        Returns:
            list[Metadata]: The success metadata based on the function name.
        """
        raise NotImplementedError

    @abstractmethod
    def _read_parquet_to_dataframe(self, file_path: str) -> pd.DataFrame:  # pragma: no cover
        """
        Read parquet file from the given file path.

        Args:
            file_path (str): The file path to read the parquet file.
        Returns:
            pd.DataFrame: The read parquet file.
        """
        raise NotImplementedError

    @abstractmethod
    def _read_csv_to_dataframe(self, file_path: str) -> pd.DataFrame:  # pragma: no cover
        """
        Read csv file from the given file path.

        Args:
            file_path (str): The file path to read the csv file.
        Returns:
            pd.DataFrame: The read csv file.
        """
        raise NotImplementedError

    @abstractmethod
    def _read_pickle(self, file_path: str) -> Any:  # pragma: no cover
        """
        Read pickle file from the given file path.

        Args:
            file_path (str): The file path to read the pickle file.
        Returns:
            Any: The read pickle file.
        """
        raise NotImplementedError

    @abstractmethod
    def _read_text(self, file_path: str) -> Any:  # pragma: no cover
        """
        Read pickle file from the given file path.

        Args:
            file_path (str): The file path to read the pickle file.
        Returns:
            Any: The read pickle file.
        """
        raise NotImplementedError

    @abstractmethod
    def _read_json(self, file_path: str) -> Any:  # pragma: no cover
        """
        Read json file from the given file path.

        Args:
            file_path (str): The file path to read the json file.
        Returns:
            Any: The read json file.
        """
        raise NotImplementedError

    def read_result(self, metadata: MetadataSuccess) -> Any:
        """
        Read the result based on the metadata.

        Args:
            metadata (MetadataSuccess): The metadata to read the result.
        Returns:
            Any: The read result.
        """
        file_path: str = metadata.result_path
        result_type: str = metadata.result_type
        need_cast: bool = False

        if "DataFrame" in result_type:
            if file_path.endswith(".gz"):
                func = self._read_parquet_to_dataframe
            elif file_path.endswith(".csv"):
                func = self._read_csv_to_dataframe
            else:
                raise NotImplementedError(f"Unsupported result type: {result_type}")
        elif file_path.endswith(".txt"):
            need_cast: bool = True
            func = self._read_text
        elif file_path.endswith(".json"):
            func = self._read_json
        elif file_path.endswith(".pkl"):
            func = self._read_pickle
        else:
            raise NotImplementedError(f"Unsupported result type: {result_type}")

        result = func(file_path)
        if need_cast:
            var_type = eval(result_type)
            result = var_type(result)
        return result

    @abstractmethod
    def _save_dataframe_to_csv(self, result: pd.DataFrame, result_path: str) -> None:  # pragma: no cover
        """
        Save dataframe to csv file from the given result and result path.

        Args:
            result (pd.DataFrame): The result.
            result_path (str): The result path.
        """
        raise NotImplementedError

    @abstractmethod
    def _save_dataframe_to_parquet(self, result: pd.DataFrame, result_path: str) -> None:  # pragma: no cover
        """
        Save dataframe to parquet file from the given result and result path.

        Args:
            result (pd.DataFrame): The result.
            result_path (str): The result path.
        """
        raise NotImplementedError

    @abstractmethod
    def _save_to_pickle(self, result: Any, result_path: str) -> None:  # pragma: no cover
        """
        Save pickle file from the given result and result path.

        Args:
            result (Any): The result.
            result_path (str): The result path.
        """
        raise NotImplementedError

    @abstractmethod
    def _save_to_text(self, result: Any, result_path: str) -> None:  # pragma: no cover
        """
        Save text file from the given result and result path.

        Args:
            result (Any): The result.
            result_path (str): The result path.
        """
        raise NotImplementedError

    @abstractmethod
    def _save_to_json(self, result: Any, result_path: str) -> None:  # pragma: no cover
        """
        Save json file from the given result and result path.

        Args:
            result (Any): The result.
            result_path (str): The result path.
        """
        raise NotImplementedError

    def save_result(
        self,
        func_name: str,
        result: Any,
        output_folder: str,
        output_format: str | None = None,
    ) -> tuple[str, datetime]:
        """
        Save the result based on the function name and result.

        Args:
            func_name (str): The function name.
            result (Any): The result to save.
            output_folder (str): The output folder.
            output_format (str | None): The output format.
        Returns:
            tuple[str, datetime]: The result path and event time.
        """
        if type(result) is pd.DataFrame:
            if output_format == "csv":
                func = self._save_dataframe_to_csv
            else:
                output_format = "parquet.gz"
                func = self._save_dataframe_to_parquet
        elif output_format == "txt":
            func = self._save_to_text
        elif output_format == "json":
            func = self._save_to_json
        else:
            output_format = "pkl"
            func = self._save_to_pickle

        event_time: datetime = datetime.now()
        result_path = self.result_path(func_name, event_time, output_folder, output_format)
        func(result=result, result_path=result_path)
        return result_path, event_time

    @abstractmethod
    def _write_metadata(self, metadata_path: str, metadata: Metadata) -> None:  # pragma: no cover
        """
        Write metadata to the given metadata path.

        Args:
            metadata_path (Path): The metadata path to write the metadata.
            metadata (Metadata): The metadata to write.
        """
        raise NotImplementedError

    def _save_metadata(self, func_name: str, metadata: Metadata, output_folder: str) -> None:
        """
        Save the metadata based on the function name and metadata.

        Args:
            func_name (str): The function name.
            metadata (Metadata): The metadata to save.
            output_folder (str): The output folder.
        """
        metadata_path: str = self.metadata_path(func_name, metadata.event_time, output_folder)
        self._write_metadata(metadata_path, metadata)

    def save_success_metadata(
        self,
        func_name: str,
        output_folder: str,
        hashed_arguments: str,
        event_time: datetime,
        result_path: str,
        result_type: str,
        extra_metadata: dict,
    ) -> None:
        """
        Save success metadata based on the function name, arguments, event time, and result path.

        Args:
            func_name (str): The function name.
            output_folder (str): The output folder.
            hashed_arguments (str): The hashed arguments.
            event_time (datetime): The event time.
            result_path (str): The result path.
            result_type (str): The result type.
            extra_metadata (dict): The extra metadata.
        """
        metadata = MetadataSuccess(
            status=Status.SUCCESS,
            event_time=event_time,
            hashed_arguments=hashed_arguments,
            result_path=result_path,
            result_type=result_type,
            extra_metadata=extra_metadata,
        )
        self._save_metadata(func_name, metadata, output_folder)

    def save_failed_metadata(
        self,
        func_name: str,
        output_folder: str,
        hashed_arguments: str,
        event_time: datetime,
        error_message: str,
        data: dict,
        extra_metadata: dict,
    ) -> None:
        """
        Save failed metadata based on the function name, arguments, event time, error message, and data.

        Args:
            func_name (str): The function name.
            output_folder (str): The output folder.
            hashed_arguments (str): The function's hashed arguments.
            event_time (datetime): The event time.
            error_message (str): The error message.
            data (dict): The data to save.
        """
        metadata = MetadataFail(
            status=Status.FAIL,
            event_time=event_time,
            hashed_arguments=hashed_arguments,
            error_message=error_message,
            data=data,
            extra_metadata=extra_metadata,
        )
        self._save_metadata(func_name, metadata, output_folder)
