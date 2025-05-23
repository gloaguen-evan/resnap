import time
from pathlib import Path

import pandas as pd
import toml
from constants import FILES, TEST_CONFIG_GLOBAL
from job_test import run_job

TEST_CONFIG_LOCAL = TEST_CONFIG_GLOBAL.copy()
RESULT_PATH = Path(toml.load("pyproject.toml")["tool"]["resnap"]["output_base_path"])


def execution_no_previous_save() -> list[Path]:
    run_job(conf_test=TEST_CONFIG_LOCAL)

    generated_files = list(RESULT_PATH.rglob("*.resnap*"))
    for file in generated_files:
        if not [f for f in FILES if f in file.name]:
            assert False, "No file was generated"

    assert len(generated_files) == len(FILES) * 2, "Not all files were generated"
    return generated_files


def execution_with_previous_save_same_config(last_generated_files: list[Path]) -> None:
    generated_files = execution_no_previous_save()
    assert sorted(generated_files) == sorted(last_generated_files), "Don't use resnap"


def execution_with_previous_save_different_config(last_generated_files: list[Path]) -> list[Path]:
    config = TEST_CONFIG_LOCAL.copy()
    config["first_method_argument"] = pd.DataFrame(
        {
            "C": [1, 2, 3],
            "D": [4, 5, 6],
            "E": [7, 8, 9],
        }
    )
    config["second_method_argument"] = "toto"
    config["third_method_argument"] = "tata"
    config["BasicClass_get_param_value_argument"] = "toto"
    config["BasicClass_generate_dataframe_argument"] = "toto"
    config["a_function_argument"] = False
    run_job(conf_test=config)

    generated_files = list(RESULT_PATH.rglob("*.resnap*"))
    new_files = []
    for file in generated_files:
        if [f for f in FILES if f in file.name and file not in last_generated_files]:
            new_files.append(file)

    if not new_files:
        assert False, "No file was generated"

    assert len(generated_files) == len(FILES) * 4, "Not all files were generated"
    assert len(new_files) == len(FILES) * 2, "Not all files were generated"
    assert sorted(new_files) != sorted(last_generated_files), "Don't use resnap"
    return new_files


def execution_with_clean(last_generated_files: list[Path]) -> None:
    generated_files = execution_no_previous_save()
    assert sorted(generated_files) != sorted(last_generated_files), "Don't clean old files"
    assert len(generated_files) == len(FILES) * 2, "Not all files were generated"


def clear_project(path: Path = RESULT_PATH) -> None:
    if not path.exists():
        return
    for file in path.iterdir():
        if file.is_file():
            file.unlink()
        else:
            clear_project(file)
    path.rmdir()


def run() -> None:
    print()
    print("**** START TESTS LOCAL SERVICE ****")
    clear_project()

    print("Running test: first execution with no save")
    generated_files = execution_no_previous_save()
    print("Test passed")
    print("-" * 25)

    print("Running test: execution with save and same configuration")
    execution_with_previous_save_same_config(generated_files)
    print("Test passed")
    print("-" * 25)

    print("Running test: execution with save and different configuration")
    generated_files = execution_with_previous_save_different_config(generated_files)
    print("Test passed")
    print("-" * 25)
    time.sleep(3)

    print("Running test: execution with same configuration, must clean old files")
    execution_with_clean(generated_files)
    print("Test passed")
    print("-" * 25)

    print("Cleaning files generated by tests")
    clear_project()
    print("-" * 25)

    print("**** END TESTS LOCAL SERVICE ****")
