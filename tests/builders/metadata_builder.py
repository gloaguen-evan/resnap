from abc import ABC
from datetime import datetime
from typing import Any

from typing_extensions import Self

from resnap.helpers.metadata import MetadataFail, MetadataSuccess
from resnap.helpers.status import Status
from resnap.helpers.utils import hash_arguments


class MetadataBuilder(ABC):
    _event_time: datetime = datetime.fromisoformat("2021-01-01T00:00:00")
    _hashed_arguments: str = ""
    _extra_metadata: dict[str, Any] = {}

    @classmethod
    def a_metadata(cls) -> Self:
        return cls()

    def with_event_time(self, event_time: datetime) -> Self:
        self._event_time = event_time
        return self

    def with_arguments(self, arguments: dict[str, Any]) -> Self:
        self._hashed_arguments = hash_arguments(arguments)
        return self

    def with_extra_metadata(self, extra_metadata: dict[str, Any]) -> Self:
        self._extra_metadata = extra_metadata
        return self


class MetadataSuccessBuilder(MetadataBuilder):
    _status: Status = Status.SUCCESS
    _result_path: str = "/path/to/result"
    _result_type: str = "str"

    def with_result_path(self, result_path: str) -> Self:
        self._result_path = result_path
        return self

    def with_result_type(self, result_type: str) -> Self:
        self._result_type = result_type
        return

    def build(self) -> MetadataSuccess:
        return MetadataSuccess(
            status=self._status,
            event_time=self._event_time,
            hashed_arguments=self._hashed_arguments,
            result_path=self._result_path,
            result_type=self._result_type,
            extra_metadata=self._extra_metadata,
        )


class MetadataFailBuilder(MetadataBuilder):
    _status: Status = Status.FAIL
    _error_message: str = ""
    _data: dict = {}

    def with_error_message(self, error_message: str) -> Self:
        self._error_message = error_message
        return self

    def with_data(self, data: dict) -> Self:
        self._data = data
        return self

    def build(self) -> MetadataFail:
        return MetadataFail(
            status=self._status,
            event_time=self._event_time,
            hashed_arguments=self._hashed_arguments,
            error_message=self._error_message,
            data=self._data,
            extra_metadata=self._extra_metadata,
        )
