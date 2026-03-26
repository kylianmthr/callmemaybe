from src import parsing
from src.__main__ import answer_prompt
from llm_sdk import llm_sdk
import pytest


@pytest.mark.parametrize(
    "prompt, expected_output",
    [
        # (
        #    "Read C:\\Users\\john\\config.ini with latin-1 encoding",
        #    {
        #        "prompt": "Read C:\\Users\\john\\config.ini with latin-1 encoding",
        #        "name": "fn_read_file",
        #        "parameters": {
        #            "path": "C:\\Users\\john\\config.ini",
        #            "encoding": "latin-1",
        #        },
        #    },
        # ),
        (
            'Format template: Say "hello" to {name}',
            {
                "prompt": 'Format template: Say "hello" to {name}',
                "name": "fn_format_template",
                "parameters": {"template": 'Say "hello" to {name}'},
            },
        ),
    ],
)
def test_regex_prompt(prompt: str, expected_output: dict):
    llm = llm_sdk.Small_LLM_Model()
    functions = parsing.parse_json_object(
        parsing.file_to_functions_object("tests/moulinette_definition.json")
    )
    generated_dictionnary = answer_prompt(llm, prompt, functions)
    print(generated_dictionnary)
    assert generated_dictionnary == expected_output
