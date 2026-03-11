from src import parsing
from src.__main__ import answer_prompt
from src.llm_sdk import llm_sdk
import pytest


@pytest.mark.parametrize(
    "prompt, expected_output",
    [
        (
            (
                'Replace all numbers in "Hello 34 I\'m 233 years old" '
                "with NUMBERS"
            ),
            {
                "prompt": (
                    'Replace all numbers in "Hello 34 I\'m 233 years old" with'
                    "NUMBERS"
                ),
                "name": "fn_substitute_string_with_regex",
                "parameters": {
                    "source_string": "Hello 34 I'm 233 years old",
                    "regex": r"\d+",
                    "replacement": "NUMBERS",
                },
            },
        ),
        (
            "Replace all vowels in 'Programming is fun' with asterisks",
            {
                "prompt": (
                    "Replace all vowels in 'Programming is fun' with asterisks"
                ),
                "name": "fn_substitute_string_with_regex",
                "parameters": {
                    "source_string": "Programming is fun",
                    "regex": r"[aeiouAEIOU]",
                    "replacement": "*",
                },
            },
        ),
        (
            (
                "Substitute the word 'cat' with 'dog' in 'The cat sat on the "
                "mat with another cat'"
            ),
            {
                "prompt": (
                    "Substitute the word 'cat' with 'dog' in 'The cat "
                    "sat on the mat with another cat'"
                ),
                "name": "fn_substitute_string_with_regex",
                "parameters": {
                    "source_string": "The cat sat on the mat with another cat",
                    "regex": r"\bcat\b",
                    "replacement": "dog",
                },
            },
        ),
        (
            "What is the sum of 2 and 3?",
            {
                "prompt": "What is the sum of 2 and 3?",
                "name": "fn_add_numbers",
                "parameters": {
                    "a": "2",
                    "b": "3",
                },
            },
        ),
        (
            "What is the sum of 265 and 345?",
            {
                "prompt": "What is the sum of 265 and 345?",
                "name": "fn_add_numbers",
                "parameters": {
                    "a": "265",
                    "b": "345",
                },
            },
        ),
        (
            "Greet shrek",
            {
                "prompt": "Greet shrek",
                "name": "fn_greet",
                "parameters": {
                    "name": "shrek",
                },
            },
        ),
        (
            "Greet john",
            {
                "prompt": "Greet john",
                "name": "fn_greet",
                "parameters": {
                    "name": "john",
                },
            },
        ),
        (
            "Reverse the string 'hello'",
            {
                "prompt": "Reverse the string 'hello'",
                "name": "fn_reverse_string",
                "parameters": {
                    "s": "hello",
                },
            },
        ),
        (
            "Reverse the string 'world'",
            {
                "prompt": "Reverse the string 'world'",
                "name": "fn_reverse_string",
                "parameters": {
                    "s": "world",
                },
            },
        ),
        (
            "What is the square root of 16?",
            {
                "prompt": "What is the square root of 16?",
                "name": "fn_get_square_root",
                "parameters": {
                    "a": "16",
                },
            },
        ),
        (
            "Calculate the square root of 144",
            {
                "prompt": "Calculate the square root of 144",
                "name": "fn_get_square_root",
                "parameters": {
                    "a": "144",
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
