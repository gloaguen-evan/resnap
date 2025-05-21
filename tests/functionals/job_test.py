import asyncio
from typing import Any

from container import JobContainer
from dependency_injector.wiring import Provide, inject


@inject
async def run_pipeline(conf_test: dict[str, Any], pipeline=Provide[JobContainer.pipeline]) -> None:
    await pipeline.run(
        first_method_argument=conf_test["first_method_argument"],
        second_method_argument=conf_test["second_method_argument"],
        third_method_argument=conf_test["third_method_argument"],
        basic_class_get_param_value_argument=conf_test["BasicClass_get_param_value_argument"],
        basic_class_generate_dataframe_argument=conf_test["BasicClass_generate_dataframe_argument"],
        a_function_argument=conf_test["a_function_argument"],
    )


def run_job(conf_test: dict[str, Any]) -> None:
    try:
        container: JobContainer = JobContainer()
        conf = {"test": {"test": True}}
        container.job_config.from_dict(conf)
        container.wire(
            modules=[
                __name__,
                "pipeline",
            ]
        )
        asyncio.run(run_pipeline(conf_test))
    except Exception as err:
        raise err
