import json
from typing import TypedDict
from src.validator import (
    FunctionsDefinitionDict,
    FunctionsDefinitionValidator,
    ParametersValidator,
)


def file_to_json_object(filename: str) -> list[FunctionsDefinitionDict]:
    with open(filename, "r") as f:
        content = f.read()
        json_object: list[FunctionsDefinitionDict] = json.loads(content)
        return json_object


class ParameterDict(TypedDict):
    name: str
    type: str


def parse_json_object(
    json_object: list[FunctionsDefinitionDict],
) -> list[FunctionsDefinitionDict]:
    functions_definition = []
    for function in json_object:
        parameters: list[ParametersValidator] = []
        for param in function["parameters"]:
            parameters.append(
                ParametersValidator(
                    name=param, type=function["parameters"][param]["type"]
                )
            )
            functions_definition.append(
                FunctionsDefinitionValidator(
                    function_name=function["name"],
                    description=function["description"],
                    parameters=parameters,
                    return_type=function["returns"]["type"],
                )
            )
    return functions_definition
