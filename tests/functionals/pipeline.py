import asyncio
from datetime import datetime

import pandas as pd
from dependency_injector.wiring import Provide, inject

from resnap import ResnapError, async_resnap, resnap

exec_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


@resnap
def a_function(is_enable: bool) -> bool:
    return not is_enable


class BasicClass:
    @classmethod
    @resnap(output_format="txt")
    def get_param_value(cls, titi: str = "titi") -> str:
        return titi

    @classmethod
    @resnap
    def generate_dataframe(cls, titi: str = "titi") -> pd.DataFrame:
        return pd.DataFrame(
            {
                "A": [1, 2, 3],
                "B": [4, 5, 6],
                "C": [7, 8, 9],
            }
        )


class Pipeline:
    attribut_classe = "valeur"

    def __init__(self, titi: str = "valeur") -> None:
        self.attribut_instance = titi

    async def run(
        self,
        first_method_argument: pd.DataFrame | None = None,
        second_method_argument: str = "titi",
        third_method_argument: str = "titi",
        basic_class_get_param_value_argument: str = "titi",
        basic_class_generate_dataframe_argument: str = "titi",
        a_function_argument: bool = True,
    ) -> None:
        self._first_method(first_method_argument)
        await self._second_method(second_method_argument)
        BasicClass.get_param_value(basic_class_get_param_value_argument)
        BasicClass.generate_dataframe(basic_class_generate_dataframe_argument)
        a_function(a_function_argument)
        self._third_method(third_method_argument)

    @resnap(output_format="csv", output_folder=f"toto_{exec_time}")
    @inject
    def _first_method(self, df: pd.DataFrame | None = None, test=Provide["test"]) -> pd.DataFrame:
        if df is not None:
            return df
        return pd.DataFrame(
            {
                "A": [1, 2, 3],
                "B": [4, 5, 6],
                "C": [7, 8, 9],
            }
        )

    @async_resnap(output_format="txt")
    async def _second_method(self, titi: str = "titi") -> str:
        await asyncio.sleep(0.1)
        return titi

    @staticmethod
    @resnap(output_format="json", output_folder="test")
    def _third_method(titi: str = "titi") -> dict:
        if titi == "toto":
            raise ResnapError("toto is not allowed", data={"titi": titi})
        return {"tata": titi}
