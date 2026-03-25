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
    """
    Parses command-line arguments for the script.

    Returns:
        argparse.Namespace: An object containing the parsed command-line
        arguments:
            --functions_definition (str): Path to the file with function
                definitions used to respond to prompts.
            --input (str): Path to the file containing prompts.
            --output (str): Path to the file where the generated function
                call will be saved.
    """
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
    """
    Reads a JSON file containing a list of function definitions and returns
    it as a list of FunctionsDefinitionDict objects.

    Args:
        filename (str): The path to the JSON file to read.

    Returns:
        list[FunctionsDefinitionDict]: A list of function definition
        dictionaries parsed from the file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file content is not valid JSON.
    """
    with open(filename, "r") as f:
        content = f.read()
        json_object: list[FunctionsDefinitionDict] = json.loads(content)
        return json_object


def file_to_prompts_object(
    filename: str,
) -> list[PromptsDict]:
    """
    Reads a JSON file containing a list of prompt dictionaries and returns
    it as a list of PromptsDict objects.

    Args:
        filename (str): The path to the JSON file to be read.

    Returns:
        list[PromptsDict]: A list of prompt dictionaries loaded from the file.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file content is not valid JSON.
    """
    with open(filename, "r") as f:
        content = f.read()
        json_object: list[PromptsDict] = json.loads(content)
        return json_object


class ParameterDict(TypedDict):
    """
    A TypedDict representing a parameter with its name and type.

    Attributes:
        name (str): The name of the parameter.
        type (str): The type of the parameter.
    """

    name: str
    type: str


def parse_json_object(
    json_object: list[FunctionsDefinitionDict],
) -> list[FunctionsDefinitionValidator]:
    """
    Parses a list of function definition dictionaries and validates
    their structure.

    Args:
        json_object (list[FunctionsDefinitionDict]): A list of dictionaries,
            each representing a function definition with keys such as "name",
            "description", "parameters", and "returns".

    Returns:
        list[FunctionsDefinitionValidator]: A list of validated
            function definitions, each represented as a
            FunctionsDefinitionValidator instance.

    Raises:
        ValueError: If an unexpected key is found in a function
            definition dictionary.
    """
    functions_definition = []
    for function in json_object:
        parameters: list[ParametersValidator] = []
        for param in function["parameters"]:
            parameters.append(
                ParametersValidator(
                    name=param, type=function["parameters"][param]["type"]
                )
            )
        for param in function:
            if param not in ["name", "description", "returns", "type"]:
                raise ValueError(
                    "Unexpected format, found unexpected key:", param
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
    """
    Parses a list of prompt dictionaries and returns a list of PromptValidator
    objects.

    Args:
        json_object (list[PromptsDict]): A list of dictionaries, each
            representing a prompt with a "prompt" key.

    Returns:
        list[PromptValidator]: A list of PromptValidator instances created
            from the prompt contents.

    Raises:
        ValueError: If a dictionary contains a key other than "prompt".
    """
    prompts: list[PromptValidator] = []
    for prompt in json_object:
        for value in prompt:
            if value == "prompt":
                prompts.append(PromptValidator(content=prompt["prompt"]))
            else:
                raise ValueError(
                    "Unexpected format, found unexpected key:", value
                )
    return prompts
