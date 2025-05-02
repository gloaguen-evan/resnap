import time

import pandas as pd
from constants import FILES, TEST_CONFIG_GLOBAL
from job_test import run_job

TEST_CONFIG_CEPH = TEST_CONFIG_GLOBAL.copy()
TEST_CONFIG_CEPH["config_file"] = "tests/functionals/test-ceph-config.yml"
CONFIG = load_conf(filename=TEST_CONFIG_CEPH["config_file"], key="checkpoint")
RESULT_PATH = CONFIG["output_base_path"]

CEPH_SECRETS = load_secrets(filename=CONFIG["secrets_file_name"], key="ceph")


def get_files_without_folder() -> list[str]:
    files = []
    with get_ceph_connection(**CEPH_SECRETS) as con:
        for file in list_dir_in_ceph(RESULT_PATH, con, True):
            if not file.endswith('/'):
                files.append(file)
    return files


def execution_no_previous_save() -> list[str]:
    run_job(conf_test=TEST_CONFIG_CEPH.copy())

    generated_files = get_files_without_folder()
    for file in generated_files:
        if not [f for f in FILES if f in file]:
            assert False, "No file was generated"

    assert len(generated_files) == len(FILES) * 2, "Not all files were generated"
    return generated_files


def execution_with_previous_save_same_config(last_generated_files: list[str]) -> None:
    generated_files = execution_no_previous_save()
    assert sorted(generated_files) == sorted(last_generated_files), "Don't use checkpoint"


def execution_with_previous_save_different_config(last_generated_files: list[str]) -> list[str]:
    config = TEST_CONFIG_CEPH.copy()
    config["first_method_argument"] = pd.DataFrame(
        {
            "C": [1, 2, 3],
            "D": [4, 5, 6],
            "E": [7, 8, 9],
        }
    )
    config["second_method_argument"] = "toto"
    config["third_method_argument"] = "tata"
    config["toto_toto_argument"] = "toto"
    config["toto_test_argument"] = "toto"
    config["a_function_argument"] = False
    run_job(conf_test=config)

    generated_files = get_files_without_folder()
    new_files = []
    for file in generated_files:
        if [f for f in FILES if f in file and file not in last_generated_files]:
            new_files.append(file)

    if not new_files:
        assert False, "No file was generated"

    assert len(generated_files) == len(FILES) * 4, "Not all files were generated"
    assert len(new_files) == len(FILES) * 2, "Not all files were generated"
    assert sorted(new_files) != sorted(last_generated_files), "Don't use checkpoint"
    return new_files


def execution_with_clean(last_generated_files: list[str]) -> None:
    generated_files = execution_no_previous_save()
    assert sorted(generated_files) != sorted(last_generated_files), "Don't clean old files"
    assert len(generated_files) == len(FILES) * 2, "Not all files were generated"


def clear_project() -> None:
    with get_ceph_connection(**CEPH_SECRETS) as con:
        if exists_in_ceph(RESULT_PATH + "/", con):
            rmdir_in_ceph(RESULT_PATH, con)


def run() -> None:
    print()
    print("**** START TESTS CEPH SERVICE ****")
    clear_project()

    print("Running test: execution with no save")
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
    time.sleep(60)

    print("Running test: execution with same configuration, must clean old files")
    execution_with_clean(generated_files)
    print("Test passed")
    print("-" * 25)

    print("Cleaning files generated for tests")
    clear_project()
    print("-" * 25)

    print("**** END TESTS LOCAL SERVICE ****")
