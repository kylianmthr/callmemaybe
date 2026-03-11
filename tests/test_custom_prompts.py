from src import parsing
from src.__main__ import answer_prompt
from src.llm_sdk import llm_sdk
import pytest


@pytest.mark.parametrize(
    "prompt, expected_output",
    [
        (
            "2 + 5",
            {
                "prompt": "2 + 5",
                "name": "fn_add_numbers",
                "parameters": {
                    "a": "2",
                    "b": "5",
                },
            },
        ),
    ],
)
def test_regex_prompt(prompt: str, expected_output: dict):
    llm = llm_sdk.Small_LLM_Model()
    functions = parsing.parse_json_object(
        parsing.file_to_functions_object(
            "src/data/input/functions_definition.json"
        )
    )
    generated_dictionnary = answer_prompt(llm, prompt, functions)
    assert generated_dictionnary == expected_output
