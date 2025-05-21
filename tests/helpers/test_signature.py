from typing import Any

import pytest

from resnap.helpers.signature import get_function_signature


def function_to_test(test: str = "test") -> None:
    pass


class MockClass:
    MAX_VALUE: int = 10

    def __init__(self, min_value: int = 0) -> None:
        self._min_value = min_value

    @classmethod
    def class_method(cls, test: str = "test") -> None:
        pass

    @staticmethod
    def static_method(test: str = "test", **kwargs: Any) -> None:
        pass

    def method(self, test: str = "test", **kwargs: Any) -> None:
        pass


class TestGetFunctionSignature:
    @pytest.mark.parametrize(
        "my_args, expected_result",
        [
            (("test",), {"test": "test", "MAX_VALUE": 10}),
            (("toto",), {"test": "toto", "MAX_VALUE": 10}),
            ((), {"test": "test", "MAX_VALUE": 10}),
        ],
    )
    def test_should_return_function_signature_with_class_method(self, my_args: tuple, expected_result: dict) -> None:
        # Given
        args = (MockClass, *my_args)

        # When
        signature, arguments = get_function_signature(MockClass.class_method.__func__, args, {}, ["MAX_VALUE"])

        # Then
        assert signature == "MockClass.class_method"
        assert arguments == expected_result

    @pytest.mark.parametrize(
        "my_args, expected_result",
        [
            (("test",), {"test": "test", "MAX_VALUE": 10, "_min_value": 5}),
            (("toto",), {"test": "toto", "MAX_VALUE": 10, "_min_value": 5}),
            ((), {"test": "test", "MAX_VALUE": 10, "_min_value": 5}),
        ],
    )
    def test_should_return_function_signature_with_class_method_instance(
        self,
        my_args: tuple,
        expected_result: dict,
    ) -> None:
        # Given
        args = (MockClass(5), *my_args)

        # When
        signature, arguments = get_function_signature(
            MockClass.class_method.__func__, args,
            {},
            ["MAX_VALUE", "_min_value"],
        )

        # Then
        assert signature == "MockClass.class_method"
        assert arguments == expected_result

    @pytest.mark.parametrize(
        "my_args, my_kwargs, expected_result",
        [
            (("test",), {"titi": 1}, {"test": "test", "kwargs": {"titi": 1}}),
            (("toto",), {}, {"test": "toto", "kwargs": {}}),
            ((), {"titi": 1}, {"test": "test", "kwargs": {"titi": 1}}),
        ],
    )
    def test_should_return_function_signature_with_static_method(
        self, my_args: tuple, my_kwargs: dict, expected_result: dict
    ) -> None:
        # When
        signature, arguments = get_function_signature(MockClass.static_method, my_args, my_kwargs)

        # Then
        assert signature == "MockClass.static_method"
        assert arguments == expected_result

    def test_should_return_function_signature_with_method(self) -> None:
        # Given
        obj = MockClass()
        my_args = (obj,)
        my_kwargs = {}

        # When
        signature = get_function_signature(MockClass.method, my_args, my_kwargs, ["MAX_VALUE", "_min_value"])

        # Then
        assert signature == ("MockClass.method", {"test": "test", "kwargs": {}, "MAX_VALUE": 10, "_min_value": 0})

    def test_should_return_function_signature_with_method_without_class_attributes(self) -> None:
        # Given
        obj = MockClass()
        my_args = (obj,)
        my_kwargs = {}

        # When
        signature = get_function_signature(MockClass.method, my_args, my_kwargs)

        # Then
        assert signature == ("MockClass.method", {"test": "test", "kwargs": {}})

    def test_should_return_function_signature_with_function(self) -> None:
        # Given
        args = ()
        kwargs = {}

        # When
        signature = get_function_signature(function_to_test, args, kwargs)

        # Then
        assert signature == ("function_to_test", {"test": "test"})
