import pytest
from src.parsing import parse_json_object
from src.validator import (
    FunctionsDefinitionDict,
    FunctionsDefinitionValidator,
    ParametersValidator,
    ReturnsDict,
)


def test_basic_function_def():
    returns: ReturnsDict = {"type": "number"}
    obj: FunctionsDefinitionDict = {
        "name": "test",
        "description": "description test",
        "parameters": {"name": {"type": "string"}, "b": {"type": "number"}},
        "returns": returns,
    }
    res = parse_json_object([obj])
    expected_parameter_obj = [
        ParametersValidator(name="name", type="string"),
        ParametersValidator(name="b", type="number"),
    ]
    expected_obj = FunctionsDefinitionValidator(
        function_name="test",
        description="description test",
        parameters=expected_parameter_obj,
        return_type="number",
    )
    assert res == [expected_obj]


def test_invalid_function_def():
    returns: ReturnsDict = {"type": "number"}
    obj: FunctionsDefinitionDict = {
        "name": "test",
        "description": "description test",
        "parameters": {"name": {"jsp": "string"}, "b": {"type": "number"}},
        "returns": returns,
    }
    with pytest.raises(Exception):
        parse_json_object([obj])
