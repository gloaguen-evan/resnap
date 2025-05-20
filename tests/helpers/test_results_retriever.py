from unittest.mock import MagicMock

import pytest

from resnap.helpers.results_retriever import ResultsRetriever
from tests.builders.metadata_builder import MetadataSuccessBuilder


@pytest.fixture
def mock_service(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch("resnap.helpers.results_retriever.ResnapService", return_value=MagicMock())
    return mock


@pytest.fixture
def mock_get_function_signature(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch("resnap.helpers.results_retriever.get_function_signature")
    return mock


@pytest.fixture
def mock_hash_arguments(mocker) -> MagicMock:
    mock: MagicMock = mocker.patch("resnap.helpers.results_retriever.hash_arguments")
    return mock


class TestResultsRetriever:
    def test_should_not_return_results_if_recovery_is_disabled(self, mock_service: MagicMock) -> None:
        # Given
        retriever = ResultsRetriever(mock_service(), {"enable_recovery": False})

        # When
        result, is_recovery = retriever._get_saved_result()

        # Then
        assert result is None
        assert not is_recovery
        mock_service.return_value.read_result.assert_not_called()

    def test_should_not_return_results__if_no_metadatas(self, mock_service: MagicMock) -> None:
        # Given
        retriever = ResultsRetriever(mock_service(), {"enable_recovery": True})
        mock_service.return_value.get_success_metadatas.return_value = []

        # When
        result, is_recovery = retriever._get_saved_result()

        # Then
        assert result is None
        assert not is_recovery
        mock_service.return_value.get_success_metadatas.assert_called_once()
        mock_service.return_value.read_result.assert_not_called()

    def test_should_not_check_arguments_if_disabled(self, mock_service: MagicMock) -> None:
        # Given
        retriever = ResultsRetriever(mock_service(), {"enable_recovery": True, "consider_args": False})
        metadata = MetadataSuccessBuilder.a_metadata().with_arguments({"magic_number": 30}).build()
        mock_service.return_value.get_success_metadatas.return_value = [metadata]
        mock_service.return_value.read_result.return_value = 30

        # When
        result, is_recovery = retriever._get_saved_result()

        # Then
        assert result == 30
        assert is_recovery is True
        mock_service.return_value.read_result.assert_called_once_with(metadata)
        mock_service.return_value.save_result.assert_not_called()

    def test_should_return_results_if_arguments_match(self, mock_service: MagicMock) -> None:
        # Given
        retriever = ResultsRetriever(mock_service(), {})
        expected_metadata = MetadataSuccessBuilder.a_metadata().with_arguments({"magic_number": 30}).build()
        other_metadata = MetadataSuccessBuilder.a_metadata().with_arguments({"magic_number": 666}).build()
        retriever.hashed_arguments = expected_metadata.hashed_arguments
        mock_service.return_value.get_success_metadatas.return_value = [other_metadata, expected_metadata]
        mock_service.return_value.read_result.return_value = 30

        # When
        result, is_recovery = retriever._get_saved_result()

        # Then
        assert result == 30
        assert is_recovery is True
        mock_service.return_value.read_result.assert_called_once_with(expected_metadata)

    def test_should_not_return_results_if_arguments_not_match(self, mock_service: MagicMock) -> None:
        # Given
        retriever = ResultsRetriever(mock_service(), {})
        metadata = MetadataSuccessBuilder.a_metadata().with_arguments({"magic_number": 30}).build()
        retriever.hashed_arguments = "toto"
        mock_service.return_value.get_success_metadatas.return_value = [metadata]

        # When
        result, is_recovery = retriever._get_saved_result()

        # Then
        assert result is None
        assert is_recovery is False
        mock_service.return_value.read_result.assert_not_called()

    def test_should_return_saved_result(
        self,
        mock_service: MagicMock,
        mock_get_function_signature: MagicMock,
        mock_hash_arguments: MagicMock,
    ) -> None:
        # Given
        def func() -> None:
            pass

        retriever = ResultsRetriever(mock_service(), {"enable_recovery": False, "output_folder": "folder_name"})
        mock_get_function_signature.return_value = ("func_name", {"arg_1": 1, "arg_2": "value"})
        mock_hash_arguments.return_value = "hashed_arguments"

        # When
        result, is_recovery = retriever.get_results(func, (1,), {})

        # Then
        assert result is None
        assert not is_recovery
        mock_service.return_value.create_output_folder.assert_called_once_with("folder_name")
        mock_get_function_signature.assert_called_once_with(func, (1,), {}, [])
        mock_hash_arguments.assert_called_once_with({"arg_1": 1, "arg_2": "value"})
