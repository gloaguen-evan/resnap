import json
import threading
from pathlib import Path
from typing import Any

import toml

from resnap import add_metadata, add_metadatas, resnap

RESULT_PATH = Path(toml.load("pyproject.toml")["tool"]["resnap"]["output_base_path"])


def get_extra_metadata_in_resnap_file(key: str) -> dict[str, Any]:
    for f in RESULT_PATH.iterdir():
        if not f.is_file() or not f.name.endswith(".resnap"):
            continue
        with open(f, "r") as json_file:
            metadata = json.load(json_file)
            assert "extra_metadata" in metadata, (
                "extra_metadata key not found in resnap file"
            )
            if key in metadata["extra_metadata"]:
                return metadata["extra_metadata"]
    else:
        assert False, f"Resnap file not found for key {key}"


@resnap
def add_metadata_test(key: str = "test", value: Any = "value") -> None:
    add_metadata(key, value)


@resnap
def add_metadatas_test() -> None:
    metadatas = {
        "f": "foo",
        "b": "bar",
    }
    add_metadatas(metadatas)


def test_add_metadata() -> None:
    add_metadata_test()
    assert get_extra_metadata_in_resnap_file("test") == {"test": "value"}


def test_add_metadatas() -> None:
    add_metadatas_test()
    assert get_extra_metadata_in_resnap_file("f") == {"f": "foo", "b": "bar"}


def test_thread_metadata_isolation() -> None:
    threads = [
        threading.Thread(target=add_metadata_test, args=("x", "foo")),
        threading.Thread(target=add_metadata_test, args=("y", "bar")),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert get_extra_metadata_in_resnap_file("x") == {"x": "foo"}
    assert get_extra_metadata_in_resnap_file("y") == {"y": "bar"}


def clear_project(path: Path = RESULT_PATH) -> None:
    if not RESULT_PATH.exists():
        return
    for file in path.iterdir():
        if file.is_file():
            file.unlink()
        else:
            clear_project(file)
    path.rmdir()


def run() -> None:
    print()
    print("**** START TESTS ADD METADATA ****")
    clear_project()

    print("Running test: execution with add_metadata")
    test_add_metadata()
    print("Test passed")
    print("-" * 25)

    print("Running test: execution with add_metadatas")
    test_add_metadatas()
    print("Test passed")
    print("-" * 25)

    print("Running test: execution with add_metadata in threads")
    test_thread_metadata_isolation()
    print("Test passed")
    print("-" * 25)

    print("Cleaning files generated for tests")
    clear_project()
    print("-" * 25)

    print("**** END TESTS ADD METADATA ****")
