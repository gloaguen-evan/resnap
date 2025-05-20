import logging
from typing import Any, Callable

from ..services.service import ResnapService
from .metadata import Metadata
from .signature import get_function_signature
from .utils import hash_arguments

logger = logging.getLogger("resnap")


class ResultsRetriever:
    def __init__(self, service: ResnapService, options: dict[str, Any]) -> None:
        self._service = service
        self._considered_attributes: list[str] = options.get("considered_attributes", [])
        self._enable_recovery: bool = options.get("enable_recovery", True)
        self._consider_args: bool = options.get("consider_args", True)

        self.output_folder: str = options.get("output_folder", "")
        self.func_name: str = ""
        self.hashed_arguments: str = ""

    def get_results(self, func: Callable, args: tuple, kwargs: dict) -> tuple[Any, bool]:
        """
        Get the results from the resnap service.

        Args:
            func (Callable): The function to get the signature from.
            args (tuple): The arguments passed to the function.
            kwargs (dict): The keyword arguments passed to the function.

        Returns:
            tuple[Any, bool]: The result of the function and a boolean indicating if the result was recovered.
        """
        self._service.create_output_folder(self.output_folder)
        self.func_name, arguments = get_function_signature(func, args, kwargs, self._considered_attributes)
        self.hashed_arguments: str = hash_arguments(arguments)
        return self._get_saved_result()

    def _get_saved_result(self) -> tuple[Any, bool]:
        if not self._enable_recovery:
            return None, False

        metadatas: list[Metadata] = self._service.get_success_metadatas(self.func_name, self.output_folder)
        if not metadatas:
            return None, False

        if not self._consider_args:
            return self._service.read_result(metadatas[0]), True

        for metadata in metadatas:
            if metadata.hashed_arguments == self.hashed_arguments:
                logger.debug("Returning saved result...")
                return self._service.read_result(metadata), True

        return None, False
