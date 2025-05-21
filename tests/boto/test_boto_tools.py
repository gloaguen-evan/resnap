import pytest

from resnap.boto.tools import format_remote_path_folder_to_search, get_folders_and_files, remove_separator_at_begin


@pytest.mark.parametrize(
    "path, expected",
    [
        pytest.param("/test/path", "test/path", id="leading_slash"),
        pytest.param("test/path/", "test/path/", id="no_leading_slash"),
        pytest.param("/", "/", id="only_slash"),
    ],
)
def test_remove_separator_at_begin(path: str, expected: str) -> None:
    # When
    result = remove_separator_at_begin(path)

    # Then
    assert result == expected


@pytest.mark.parametrize(
    "path, expected",
    [
        pytest.param("/test/path", "test/path/*", id="no_trailing_slash"),
        pytest.param("test/path/", "test/path/*", id="trailing_slash"),
        pytest.param("/test/path/*", "test/path/*", id="wildcard_in_path"),
    ],
)
def test_format_remote_path_folder_to_search(path: str, expected: str) -> None:
    # When
    result = format_remote_path_folder_to_search(path)

    # Then
    assert result == expected


@pytest.mark.parametrize(
    "path, iterator, expected_result",
    [
        pytest.param(
            "test/path/*",
            [
                {
                    "Contents": [
                        {"Key": "test/path/file1.txt"},
                        {"Key": "test/path/sub_path/"},
                    ]
                },
                {"CommonPrefixes": [{"Prefix": "test/path/folder1/"}]},
                {
                    "Contents": [
                        {"Key": "test/path/file2.txt"},
                        {"Key": "test/path/folder2/file2.txt"},
                    ]
                },
            ],
            (
                [
                    "test/path/folder1/",
                    "test/path/folder2/",
                    "test/path/sub_path/",
                ],
                [
                    "test/path/file1.txt",
                    "test/path/file2.txt",
                    "test/path/folder2/file2.txt",
                ],
            ),
            id="folders_and_files_without_wildcard",
        ),
        pytest.param(
            "test/path/*.txt",
            [
                {
                    "Contents": [
                        {"Key": "test/path/file1.txt"},
                        {"Key": "test/path/sub_path/"},
                    ]
                },
                {"CommonPrefixes": [{"Prefix": "test/path/folder1/"}]},
                {
                    "Contents": [
                        {"Key": "test/path/file2.csv"},
                        {"Key": "test/path/folder2/file2.json"},
                    ]
                },
            ],
            (
                [
                    "test/path/folder1/",
                    "test/path/sub_path/",
                ],
                [

                    "test/path/file1.txt",
                ],
            ),
            id="folders_and_files_with_wildcard_of_selected_type",
        ),
        pytest.param(
            "test/path/*/toto/*.txt",
            [
                {"Contents": [{"Key": "test/path/file1.txt"}]},
                {
                    "Contents": [
                        {"Key": "test/path/file2.csv"},
                        {"Key": "test/path/folder2/file2.json"},
                    ]
                },
                {
                    "Contents": [
                        {"Key": "test/path/toto/file2.csv"},
                        {"Key": "test/path/toto/file2.txt"},
                    ]
                },
            ],
            (
                [
                    "test/path/toto/",
                ],
                [
                    "test/path/toto/file2.txt",
                ],
            ),
            id="folders_and_files_with_wildcard_of_selected_type_in_one_directory",
        ),
        pytest.param(
            "test/path/*toto/*.txt",
            [
                {"Contents": [{"Key": "test/path/file1.txt"}]},
                {
                    "Contents": [
                        {"Key": "test/path/file2.csv"},
                        {"Key": "test/path/folder2/file2.json"},
                    ]
                },
                {
                    "Contents": [
                        {"Key": "test/path/toto/file2.csv"},
                        {"Key": "test/path/toto/file2.txt"},
                    ]
                },
            ],
            (
                [
                    "test/path/toto/",
                ],
                [
                    "test/path/toto/file2.txt",
                ],
            ),
            id="folders_and_files_with_wildcard_of_selected_type_in_one_directory_missing_slash",
        ),
        pytest.param(
            "/*",
            [
                {"Contents": [{"Key": "file1.txt"}]},
                {"CommonPrefixes": [{"Prefix": "folder1/"}]},
                {"Contents": [{"Key": "folder1/file2.csv"}]},
            ],
            (
                [
                    "folder1/",
                ],
                [
                    "file1.txt",
                    "folder1/file2.csv",
                ],
            ),
            id="folders_and_files_with_wildcard_in_root",
        ),
        pytest.param(
            "test/path/*",
            [
                {"Contents": []},
                {"CommonPrefixes": []},
            ],
            ([], []),
            id="empty_iterator",
        ),
    ],
)
def test_should_get_folders_and_files(path: str, iterator: list, expected_result: list[str]) -> None:
    # When
    result = get_folders_and_files(path, iterator)

    # Then
    assert result == expected_result


def test_should_raise_if_not_contents() -> None:
    # Given
    path = "test/path/*"
    iterator = [{"test": False}]

    # When / Then
    with pytest.raises(FileNotFoundError, match=r"The directory or object 'test/path/\*' doesn't exist."):
        get_folders_and_files(path, iterator)
