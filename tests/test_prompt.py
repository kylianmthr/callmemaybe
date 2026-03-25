from src import parsing
from src.__main__ import answer_prompt, convert_parameters
from llm_sdk import llm_sdk
import pytest


@pytest.mark.parametrize(
    "prompt, expected_output",
    [
        (
            (
                'Replace all numbers in "Hello 34 I\'m 233 years old" with NUMBERS'
            ),
            {
                "prompt": (
                    'Replace all numbers in "Hello 34 I\'m 233 years old" with NUMBERS'
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
def test_legacy_prompt(prompt: str, expected_output: dict):
    llm = llm_sdk.Small_LLM_Model()
    functions = parsing.parse_json_object(
        parsing.file_to_functions_object("tests/legacy_definition.json")
    )
    generated_dictionnary = answer_prompt(llm, prompt, functions)
    assert generated_dictionnary == expected_output


@pytest.mark.parametrize(
    "prompt, expected_output",
    [
        (
            "What is the product of 3 and 5?",
            {
                "prompt": "What is the product of 3 and 5?",
                "name": "fn_multiply_numbers",
                "parameters": {"a": 3.0, "b": 5.0},
            },
        ),
        (
            "What is the product of 12 and 4?",
            {
                "prompt": "What is the product of 12 and 4?",
                "name": "fn_multiply_numbers",
                "parameters": {"a": 12.0, "b": 4.0},
            },
        ),
        (
            "Is 4 an even number?",
            {
                "prompt": "Is 4 an even number?",
                "name": "fn_is_even",
                "parameters": {"n": 4},
            },
        ),
        (
            "Is 7 an even number?",
            {
                "prompt": "Is 7 an even number?",
                "name": "fn_is_even",
                "parameters": {"n": 7},
            },
        ),
        (
            "Calculate compound interest on 1234567.89 at 0.0375 rate for 23 years",
            {
                "prompt": "Calculate compound interest on 1234567.89 at 0.0375 rate for 23 years",
                "name": "fn_calculate_compound_interest",
                "parameters": {
                    "principal": 1234567.89,
                    "rate": 0.0375,
                    "years": 23,
                },
            },
        ),
        (
            "Execute SQL query 'SELECT * FROM users' on the production database",
            {
                "prompt": "Execute SQL query 'SELECT * FROM users' on the production database",
                "name": "fn_execute_sql_query",
                "parameters": {
                    "query": "SELECT * FROM users",
                    "database": "production",
                },
            },
        ),
        (
            "Run the query 'INSERT INTO logs VALUES (1, 2, 3)' on the system database",
            {
                "prompt": "Run the query 'INSERT INTO logs VALUES (1, 2, 3)' on the system database",
                "name": "fn_execute_sql_query",
                "parameters": {
                    "query": "INSERT INTO logs VALUES (1, 2, 3)",
                    "database": "system",
                },
            },
        ),
        (
            "Read the file at /home/user/data.json with utf-8 encoding",
            {
                "prompt": "Read the file at /home/user/data.json with utf-8 encoding",
                "name": "fn_read_file",
                "parameters": {
                    "path": "/home/user/data.json",
                    "encoding": "utf-8",
                },
            },
        ),
        (
            "Read C:\\Users\\john\\config.ini with latin-1 encoding",
            {
                "prompt": "Read C:\\Users\\john\\config.ini with latin-1 encoding",
                "name": "fn_read_file",
                "parameters": {
                    "path": "C:\\Users\\john\\config.ini",
                    "encoding": "latin-1",
                },
            },
        ),
        (
            "Format template: Hello {user}'s profile!",
            {
                "prompt": "Format template: Hello {user}'s profile!",
                "name": "fn_format_template",
                "parameters": {"template": "Hello {user}'s profile!"},
            },
        ),
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
def test_moulinette_prompt(prompt: str, expected_output: dict):
    llm = llm_sdk.Small_LLM_Model()
    functions = parsing.parse_json_object(
        parsing.file_to_functions_object("tests/moulinette_definition.json")
    )
    generated_dictionnary = answer_prompt(llm, prompt, functions)
    generated_dictionnary = convert_parameters(
        functions, [generated_dictionnary]
    )[0]
    assert generated_dictionnary == expected_output
