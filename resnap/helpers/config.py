import datetime
from enum import Enum
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing_extensions import Self

from .time_utils import TimeUnit, get_timezone_from_string


class Services(str, Enum):
    LOCAL = "local"
    S3 = "s3"


class Config(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    enabled: bool
    save_to: Services = Services.LOCAL
    output_base_path: str = ""
    secrets_file_name: str = ""
    enable_remove_old_files: bool = False
    max_history_files_length: int = Field(gt=0, default=3)
    max_history_files_time_unit: TimeUnit = TimeUnit.DAY
    timezone: datetime.timezone | ZoneInfo | None = None

    @field_validator("timezone", mode="before")
    def validate_timezone(cls, value: str | datetime.timezone | None) -> datetime.timezone | ZoneInfo | None:
        if not isinstance(value, str):
            return value
        return get_timezone_from_string(value)

    @model_validator(mode="after")
    def check_secrets_file_name(self) -> Self:
        if self.enabled and self.save_to != Services.LOCAL and not self.secrets_file_name:
            raise ValueError(f"secrets_file_name is required when save_to is {self.save_to.value}")
        return self
