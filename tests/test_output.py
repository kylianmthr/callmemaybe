from src import parsing
from src.__main__ import convert_parameters, generate_output_file


def test_output():
    input = [
        {
            "prompt": "What is the sum of 265 and 345?",
            "name": "fn_add_numbers",
            "parameters": {"a": "265", "b": "345"},
        }
    ]
    expectd_res = [
        {
            "prompt": "What is the sum of 265 and 345?",
            "name": "fn_add_numbers",
            "parameters": {"a": 265.0, "b": 345.0},
        }
    ]
    functions = parsing.parse_json_object(
        parsing.file_to_functions_object(
            "data/input/functions_definition.json"
        )
    )
    res = convert_parameters(functions, input)
    assert expectd_res == res
