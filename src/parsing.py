import json
from typing import TypedDict
from src.validator import (
    FunctionsDefinitionDict,
    FunctionsDefinitionValidator,
    ParametersValidator,
    PromptValidator,
    PromptsDict,
)
import argparse


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--functions_definition",
        type=str,
        help=(
            "The file containing the definitions of the functions that will "
            "be used to respond to your prompts."
        ),
    )
    parser.add_argument(
        "--input", type=str, help="The file containing your prompts."
    )
    parser.add_argument(
        "--output",
        type=str,
        help=(
            "The file that will be generated and will contain the "
            "function call."
        ),
    )
    return parser.parse_args()


def file_to_functions_object(
    filename: str,
) -> list[FunctionsDefinitionDict]:
    with open(filename, "r") as f:
        content = f.read()
        json_object: list[FunctionsDefinitionDict] = json.loads(content)
        return json_object


def file_to_prompts_object(
    filename: str,
) -> list[PromptsDict]:
    with open(filename, "r") as f:
        content = f.read()
        json_object: list[PromptsDict] = json.loads(content)
        return json_object


class ParameterDict(TypedDict):
    name: str
    type: str


def parse_json_object(
    json_object: list[FunctionsDefinitionDict],
) -> list[FunctionsDefinitionValidator]:
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


def parse_prompts(
    json_object: list[PromptsDict],
) -> list[PromptValidator]:
    prompts: list[PromptValidator] = []
    for prompt in json_object:
        prompts.append(PromptValidator(content=prompt["prompt"]))
    return prompts
