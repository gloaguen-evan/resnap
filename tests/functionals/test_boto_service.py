import time

import pandas as pd
import urllib3
from constants import FILES, TEST_CONFIG_GLOBAL
from job_test import run_job

from resnap import set_resnap_service
from resnap.boto.client import S3Client
from resnap.boto.config import S3Config
from resnap.helpers.config import Config
from resnap.helpers.utils import load_file
from resnap.services.boto_service import BotoResnapService

urllib3.disable_warnings()
RESULT_PATH = "resnap"
TEST_CONFIG_CEPH = TEST_CONFIG_GLOBAL.copy()
CONFIG = Config(**{
    "enabled": True,
    "save_to": "s3",
    "output_base_path": RESULT_PATH,
    "secrets_file_name": "boto_secrets.yml",
    "enable_remove_old_files": True,
    "max_history_files_length": 60,
    "max_history_files_time_unit": "second",
})


def set_service() -> BotoResnapService:
    set_resnap_service(BotoResnapService(CONFIG))


def get_s3_client() -> S3Client:
    config = S3Config(**load_file(CONFIG.secrets_file_name, key="resnap"))
    return S3Client(config)


def get_files_without_folder() -> list[str]:
    s3_client = get_s3_client()
    files = []
    for file in s3_client.list_objects(RESULT_PATH, True):
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
    config["BasicClass_get_param_value_argument"] = "toto"
    config["BasicClass_generate_dataframe_argument"] = "toto"
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
    s3_client = get_s3_client()
    if s3_client.object_exists(f"{RESULT_PATH}/"):
        s3_client.rmdir(RESULT_PATH)


def run() -> None:
    print()
    print("**** START TESTS CEPH SERVICE ****")
    set_service()
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
