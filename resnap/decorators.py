import functools
import logging
from collections.abc import Callable, Coroutine
from datetime import datetime
from typing import Any, ParamSpec, TypeVar

from .exceptions import ResnapError
from .factory import ResnapServiceFactory
from .helpers.context import clear_metadata, get_metadata, restore_metadata
from .helpers.results_retriever import ResultsRetriever
from .services.service import ResnapService

logger = logging.getLogger("resnap")


def _save(
    service: ResnapService,
    func_name: str,
    output_folder: str,
    hashed_arguments: str,
    result: Any,
    extra_metadata: dict,
    output_format: str | None = None,
) -> None:
    logger.debug("Saving result...")
    result_path, event_time = service.save_result(func_name, result, output_folder, output_format)
    service.save_success_metadata(
        func_name=func_name,
        output_folder=output_folder,
        hashed_arguments=hashed_arguments,
        event_time=event_time,
        result_path=result_path,
        result_type=type(result).__name__,
        extra_metadata=extra_metadata,
    )


def _clear(service: ResnapService) -> None:
    logger.debug("Clearing old saves...")
    service.clear_old_saves()


R = TypeVar("R")  # Return type
P = ParamSpec("P")  # Parameter specification


def resnap(_func: Callable[P, R] | None = None, **options: Any) -> Callable[P, R]:
    """
    Decorator to save the result of a function and return it if the function has been called with the same arguments
    before and the result was saved successfully.

    Args:
        output_format (str): The format in which the result should be saved.
            If None, the result will be saved in the default format of the service.
            Allowed formats for pd.DataFrame: "parquet" (default) and "csv".
            Allowed formats for other types: "pickle" (default), "txt" and "json".
        output_folder (str): The folder where the result should be saved.
            If None, the result will be saved in the default folder of the service.
        enable_recovery (bool): If True, the recovery system is enabled. The decorator will attempt to load the last
            saved result if the input parameters are identical. If False, the backup will be performed. Default is True.
        consider_args (bool): If True, the function arguments are considered to match the last saved result.
            If False, the arguments are ignored and only the function name is considered. Default is True.
        considered_attributes (list[str]): The list of class/instance attributes to consider when hashing the function
            arguments. Warning: Do not use __slots__ in your classes if you want to use this feature.
    """
    if _func is None:
        return functools.partial(resnap, **options)

    @functools.wraps(_func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        service: ResnapService = ResnapServiceFactory.get_service()

        if not service.is_enabled:
            return _func(*args, **kwargs)
        _clear(service)
        token = clear_metadata()

        results_retriever = ResultsRetriever(service, options)
        result, is_recovery = results_retriever.get_results(_func, args, kwargs)
        if is_recovery:
            return result

        try:
            logger.debug(f"Executing function {results_retriever.func_name}...")
            result = _func(*args, **kwargs)
            _save(
                service=service,
                func_name=results_retriever.func_name,
                output_folder=results_retriever.output_folder,
                hashed_arguments=results_retriever.hashed_arguments,
                result=result,
                extra_metadata=get_metadata(),
                output_format=options.get("output_format"),
            )
            return result

        except Exception as e:
            service.save_failed_metadata(
                func_name=results_retriever.func_name,
                output_folder=results_retriever.output_folder,
                hashed_arguments=results_retriever.hashed_arguments,
                event_time=datetime.now(),
                error_message=str(e),
                data=e.data if isinstance(e, ResnapError) else {},
                extra_metadata=get_metadata(),
            )
            raise e
        finally:
            restore_metadata(token)

    return wrapper


def async_resnap(
    _func: Callable[P, Coroutine[Any, Any, R]] | None = None,
    **options: Any,
) -> Callable[P, Coroutine[Any, Any, R]]:
    """
    Decorator to save the result of an async function and return it if the function has been called
    with the same arguments before and the result was saved successfully.

    Args:
        output_format (str): The format in which the result should be saved.
            If None, the result will be saved in the default format of the service.
            Allowed formats for pd.DataFrame: "parquet" (default) and "csv".
            Allowed formats for other types: "pickle" (default), "txt" and "json".
        output_folder (str): The folder where the result should be saved.
            If None, the result will be saved in the default folder of the service.
        enable_recovery (bool): If True, the recovery system is enabled. The decorator will attempt to load the last
            saved result if the input parameters are identical. If False, the backup will be performed. Default is True.
        consider_args (bool): If True, the function arguments are considered to match the last saved result.
            If False, the arguments are ignored and only the function name is considered. Default is True.
        considered_attributes (list[str]): The list of class/instance attributes to consider when hashing the function
            arguments.
    """
    if _func is None:
        return functools.partial(async_resnap, **options)

    @functools.wraps(_func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        service: ResnapService = ResnapServiceFactory.get_service()

        if not service.is_enabled:
            return await _func(*args, **kwargs)
        _clear(service)
        token = clear_metadata()

        results_retriever = ResultsRetriever(service, options)
        result, is_recovery = results_retriever.get_results(_func, args, kwargs)
        if is_recovery:
            return result

        try:
            logger.debug(f"Executing function {results_retriever.func_name}...")
            result = await _func(*args, **kwargs)
            _save(
                service=service,
                func_name=results_retriever.func_name,
                output_folder=results_retriever.output_folder,
                hashed_arguments=results_retriever.hashed_arguments,
                result=result,
                extra_metadata=get_metadata(),
                output_format=options.get("output_format"),
            )
            return result

        except Exception as e:
            service.save_failed_metadata(
                func_name=results_retriever.func_name,
                output_folder=results_retriever.output_folder,
                hashed_arguments=results_retriever.hashed_arguments,
                event_time=datetime.now(),
                error_message=str(e),
                data=e.data if isinstance(e, ResnapError) else {},
                extra_metadata=get_metadata(),
            )
            raise e
        finally:
            restore_metadata(token)

    return wrapper
