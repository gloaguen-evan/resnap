from dataclasses import dataclass

from typing_extensions import Self

from resnap.helpers.config import Config, Services
from resnap.helpers.utils import TimeUnit


@dataclass
class ConfigBuilder:
    _enabled: bool = True
    _save_to: Services = Services.LOCAL
    _output_base_path: str = ""
    _secrets_file_name: str = ""
    _enable_remove_old_files: bool = False
    _max_history_files_length: int = 3
    _max_history_files_time_unit: TimeUnit = TimeUnit.HOUR

    @classmethod
    def a_config(cls) -> Self:
        return cls()

    def is_enabled(self, enabled: bool) -> Self:
        self._enabled = enabled
        return self

    def save_to(self, save_to: Services) -> Self:
        self._save_to = save_to
        return self

    def with_output_base_path(self, output_base_path: str) -> Self:
        self._output_base_path = output_base_path
        return self

    def with_secrets_file_name(self, secrets_file_name: str) -> Self:
        self._secrets_file_name = secrets_file_name
        return self

    def enable_remove_old_files(self, enable_remove_old_files: bool) -> Self:
        self._enable_remove_old_files = enable_remove_old_files
        return self

    def with_max_history_files_length(self, max_history_files_length: int) -> Self:
        self._max_history_files_length = max_history_files_length
        return self

    def with_max_history_files_time_unit(self, max_history_files_time_unit: TimeUnit) -> Self:
        self._max_history_files_time_unit = max_history_files_time_unit
        return self

    def build(self) -> Config:
        return Config(
            enabled=self._enabled,
            save_to=self._save_to,
            output_base_path=self._output_base_path,
            secrets_file_name=self._secrets_file_name,
            enable_remove_old_files=self._enable_remove_old_files,
            max_history_files_length=self._max_history_files_length,
            max_history_files_time_unit=self._max_history_files_time_unit,
        )
