from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from typing_extensions import Self

from .status import Status


@dataclass(frozen=True, kw_only=True)
class Metadata(ABC):
    status: Status
    event_time: datetime
    hashed_arguments: str
    extra_metadata: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict) -> MetadataSuccess | MetadataFail:
        if data["status"] == Status.SUCCESS.value:
            return MetadataSuccess.from_dict(data)
        return MetadataFail.from_dict(data)

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class MetadataSuccess(Metadata):
    result_path: str
    result_type: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            status=Status(data["status"]),
            event_time=datetime.fromisoformat(data["event_time"]),
            hashed_arguments=data["hashed_arguments"],
            result_path=data["result_path"],
            result_type=data["result_type"],
            extra_metadata=data.get("extra_metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        metadata = {
            "status": self.status.value,
            "event_time": self.event_time.isoformat(),
            "hashed_arguments": self.hashed_arguments,
            "result_path": self.result_path,
            "result_type": self.result_type,
        }
        if self.extra_metadata:
            metadata["extra_metadata"] = self.extra_metadata
        return metadata


@dataclass(frozen=True, kw_only=True)
class MetadataFail(Metadata):
    error_message: str
    data: dict

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            status=Status(data["status"]),
            event_time=datetime.fromisoformat(data["event_time"]),
            hashed_arguments=data["hashed_arguments"],
            error_message=data["error_message"],
            data=data.get("data", {}),
            extra_metadata=data.get("extra_metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        metadata = {
            "status": self.status.value,
            "event_time": self.event_time.isoformat(),
            "hashed_arguments": self.hashed_arguments,
            "error_message": self.error_message,
        }
        if self.data:
            metadata["data"] = self.data
        if self.extra_metadata:
            metadata["extra_metadata"] = self.extra_metadata
        return metadata
