import inspect
from typing import Any, Callable


def get_function_signature(
    func: Callable,
    args: tuple,
    kwargs: dict,
    considered_attributes: list[str] = None,
) -> tuple[str, dict[str, Any]]:
    """
    Get the function name and arguments from the function signature.
    If the function is a method, the first argument is skipped and name is composed from the class and method name.

    Args:
        func (Callable): The function to get the signature from.
        args (tuple): The arguments passed to the function.
        kwargs (dict): The keyword arguments passed to the function.
        considered_attributes (list[str]): The list of class/instance attributes to consider when hashing the function
        arguments.
    Returns:
        tuple[str, dict[str, Any]]: The function name and the arguments.
    """
    considered_attributes = considered_attributes or []
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    func_name = ""
    arguments = {}
    for i, (name, value) in enumerate(bound_args.arguments.items()):
        if i == 0 and name in ("self", "cls"):
            arguments.update(get_attributes(value, considered_attributes))
            continue
        arguments[name] = value

    func_name = func.__qualname__
    return func_name, arguments


def _get_attributes(instance_attributes: dict[str, Any], considered_attributes: list[str]) -> dict[str, Any]:
    """
    Get the attributes of an instance.

    Args:
        instance (dict[str, Any]): The instance attributes.
        considered_attributes (list[str]): The list of class/instance attributes to consider when hashing the function
        arguments.
    Returns:
        dict[str, Any]: The attributes of the instance filtered.
    """
    return {
        attr: value for attr, value in instance_attributes
        if attr in considered_attributes
        and not callable(value)
        and not attr.startswith("__")
        and not isinstance(value, classmethod)
    }


def get_attributes(instance: Any, considered_attributes: list[str]) -> dict[str, Any]:
    """
    Get the attributes of an instance.

    Args:
        instance (Any): The instance to get the attributes from.
        considered_attributes (list[str]): The list of class/instance attributes to consider when hashing the function
        arguments.
    Returns:
        dict[str, Any]: The attributes of the instance.
    """
    class_attributes = _get_attributes(instance.__class__.__dict__.items(), considered_attributes)

    instance_attributes = _get_attributes(instance.__dict__.items(), considered_attributes)
    return {**class_attributes, **instance_attributes}
