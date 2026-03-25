from typing import Any, Callable, TypedDict
from pydantic import BaseModel, Field
from src.functions import (
    fn_add_numbers,
    fn_get_square_root,
    fn_greet,
    fn_reverse_string,
    fn_substitute_string_with_regex,
)

functions: dict[str, Callable[..., Any]] = {
    "fn_add_numbers": fn_add_numbers,
    "fn_greet": fn_greet,
    "fn_reverse_string": fn_reverse_string,
    "fn_get_square_root": fn_get_square_root,
    "fn_substitute_string_with_regex": fn_substitute_string_with_regex,
}


def function_validation(name: str) -> Callable[..., Any]:
    """
    Retrieves a function from the global `functions` dictionary by its name.

    Args:
        name (str): The name of the function to retrieve.

    Returns:
        Callable[..., Any]: The function object associated with the given
            name.

    Raises:
        ValueError: If the function name is not found in the `functions`
            dictionary.
    """
    if name in functions:
        return functions[name]
    raise ValueError(f"Error: {name} function not found.")


class ReturnsDict(TypedDict):
    """
    Typed dictionary representing a return value with a single key.

    Attributes:
        type (str): The type of the return value.
    """

    type: str


class FunctionsDefinitionDict(TypedDict):
    """
    TypedDict representing the definition of a function.

    Attributes:
        name (str): The name of the function.
        description (str): A brief description of the function.
        parameters (dict[str, dict[str, str]]): A dictionary mapping
            parameter names to their details, where each detail is itself a
            dictionary of string keys and values.
        returns (ReturnsDict): The return type and details of the function,
            represented by a ReturnsDict.
    """

    name: str
    description: str
    parameters: dict[str, dict[str, str]]
    returns: ReturnsDict


class PromptsDict(TypedDict):
    """
    A TypedDict representing a dictionary with a single key 'prompt'
    of type str.

    Attributes:
        prompt (str): The prompt string to be used.
    """

    prompt: str


class ParametersValidator(BaseModel):
    """
    ParametersValidator validates input parameters for a given entity.

    Attributes:
        name (str): The name of the parameter. Must be a non-empty string.
        type (str): The type of the parameter. Must be a non-empty string.
    """

    name: str = Field(min_length=1)
    type: str = Field(min_length=1)


class FunctionsDefinitionValidator(BaseModel):
    """
    Validator model for function definitions.

    Attributes:
        function_name (str): The name of the function. Must be at least
            1 character long.
        description (str): A brief description of the function. Must be at
            least 1 character long.
        parameters (list[ParametersValidator]): A list of parameter validators
            for the function's parameters.
        return_type (str): The return type of the function. Must be at least 1
            character long.
    """

    # function_name: Annotated[str, AfterValidator(function_validation)] =
    # Field(
    #    min_length=1
    # )
    function_name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    parameters: list[
        ParametersValidator
    ]  # Potentiellement check si parameters est vraiment obligatoire
    return_type: str = Field(min_length=1)


class PromptValidator(BaseModel):
    """
    PromptValidator validates that the 'content' field is a non-empty string.

    Attributes:
        content (str): The prompt content to be validated. Must have at least
            1 character.
    """

    content: str = Field(min_length=1)
