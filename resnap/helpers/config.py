from enum import Enum

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self

from .utils import TimeUnit


class Services(str, Enum):
    LOCAL = "local"
    S3 = "s3"


class Config(BaseModel):
    enabled: bool
    save_to: Services = Services.LOCAL
    output_base_path: str = ""
    secrets_file_name: str = ""
    enable_remove_old_files: bool = False
    max_history_files_length: int = Field(gt=0, default=3)
    max_history_files_time_unit: TimeUnit = TimeUnit.DAY

    @model_validator(mode="after")
    def check_secrets_file_name(self) -> Self:
        if self.save_to != Services.LOCAL and not self.secrets_file_name:
            raise ValueError(f"secrets_file_name is required when save_to is {self.save_to.value}")
        return self
