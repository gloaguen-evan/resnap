import pandas as pd

FILES = [
    "Pipeline._first_method",
    "Pipeline._second_method",
    "Pipeline._third_method",
    "BasicClass.get_param_value",
    "BasicClass.generate_dataframe",
    "a_function",
]
TEST_CONFIG_GLOBAL = {
    "first_method_argument": pd.DataFrame(
        {
            "A": [1, 2, 3],
            "B": [4, 5, 6],
            "C": [7, 8, 9],
        }
    ),
    "second_method_argument": "titi",
    "third_method_argument": "titi",
    "BasicClass_get_param_value_argument": "titi",
    "BasicClass_generate_dataframe_argument": "titi",
    "a_function_argument": True,
}
