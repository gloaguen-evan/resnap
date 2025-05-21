from botocore.paginate import PageIterator

SEPARATOR = "/"


def remove_separator_at_begin(path: str) -> str:
    """Remove the leading separator from the given path.

    Args:
        path (str): The given path.

    Returns:
        str: The path without the leading separator.
    """
    return path.lstrip(SEPARATOR) if path != SEPARATOR else path


def format_remote_path_folder_to_search(path: str) -> str:
    """Format the given path to be used in S3 search.

    Args:
        path (str): The given path.

    Returns:
        str: The formatted path.
    """
    path = remove_separator_at_begin(path)
    if not path.endswith(SEPARATOR) and not path.endswith("*"):
        path += SEPARATOR
    if "*" not in path:
        path += "*"
    return path


def get_folders_and_files(remote_dir_path: str, page_iterator: PageIterator) -> tuple[list[str], list[str]]:
    """Get the folders and files from the given page iterator.

    Args:
        remote_dir_path (str): The remote directory path.
        page_iterator (PageIterator): The page iterator.

    Returns:
        tuple[list[str], list[str]]: A tuple containing the list of folders and files.
    """
    wildcard = remote_dir_path[remote_dir_path.index("*") :]
    files: list[str] = []
    folders: list[str] = []
    for page in page_iterator:
        if "Contents" not in page and "CommonPrefixes" not in page:
            raise FileNotFoundError(f"The directory or object '{remote_dir_path}' doesn't exist.")

        folders.extend([element["Prefix"] for element in page.get("CommonPrefixes", [])])

        page_contents: list[dict] = page.get("Contents", [])

        all_filepaths: list[str] = []
        for element in page_contents:
            _current_element: str = element["Key"]

            if _current_element.endswith(SEPARATOR):
                folders.append(_current_element)
            else:
                all_filepaths.append(_current_element)

        files_filtered: list = _filter_files_according_to_wildcard(wildcard, all_filepaths)

        files.extend(files_filtered)

    folders.extend(_fill_folders_from_filepaths(files, remote_dir_path))

    return sorted(set(folders)), sorted(set(files))


def _filter_files_according_to_wildcard(wildcard: str, filepaths: list[str]) -> list[str]:
    """Find files with wildcard. Allowed wildcards are : path/to/*/[foo/bar]/[*|*.ext|file.ext]

    Args:
        wildcard (str): The wildcard to filter files.
        page_contents (List[Dict[str, str]]): Remote directory content.

    Returns:
        List[str]: Files to keep.
    """
    if not wildcard or wildcard == "*":
        return filepaths

    file_ext, directory = _split_and_format_wildcard(wildcard)
    return [file for file in filepaths if _file_must_be_included(file_ext, directory, file)]


def _file_must_be_included(file_extension: str, directory: str, file_path: str) -> bool:
    """Tell if the file must be included.

    Args:
        file_ext (str): Extension of file to keep.
        directory (str): Directory in wildcard if exists.
        file_path (str): File to filter path.

    Returns:
        bool: True if the file must be included, False otherwise.
    """
    _is_in_wildcard_with_required_extension: bool = (
        (f"{SEPARATOR}{directory}{SEPARATOR}" in file_path) or not directory
    ) and file_path.endswith(file_extension)

    return _is_in_wildcard_with_required_extension


def _split_and_format_wildcard(wildcard: str) -> tuple[str, str]:
    """Split the given wildcard and format it.

    Args:
        wildcard (str): The given wildcard.

    Returns:
        Tuple[str, str]: File extension and directory if exists.
    """
    formatted_wildcard: list = wildcard.replace("*", "").split(SEPARATOR)
    file_ext: str = formatted_wildcard[-1]
    directory: str = ""

    if len(formatted_wildcard) == 3:
        directory = formatted_wildcard[1]
    elif len(formatted_wildcard) == 2:
        directory = formatted_wildcard[0]

    return file_ext, directory


def _fill_folders_from_filepaths(files: list[str], remote_path: str) -> list[str]:
    """Used in case of unexpected behavior of boto3 paginator.
    This function fills folders list based on given filepaths information.

    Args:
        files (List[str]): Input file list.

    Returns:
        List[str]: Folder list.
    """
    if not remote_path.endswith(SEPARATOR):
        remote_path = f"{remote_path}{SEPARATOR}"

        if not remote_path.endswith("*"):
            remote_path = f"{remote_path}*"

    folders: list[str] = []
    prefix: str = remote_path[: remote_path.index("*")]

    for item in files:
        _splitted_path: list[str] = item.split(f"{prefix}{SEPARATOR}")[-1].split(SEPARATOR)
        parent_directory = _splitted_path[: len(_splitted_path) - 1]
        if not parent_directory:
            continue
        _all_subdir = f"{SEPARATOR}".join(parent_directory)
        _subdir_to_create: str = f"{_all_subdir}{SEPARATOR}"
        _equals_remote_path: bool = _subdir_to_create in prefix
        _is_already_registered: bool = _subdir_to_create in folders

        if _subdir_to_create and not _equals_remote_path and not _is_already_registered:
            folders.append(_subdir_to_create)

    return folders
