from typing import Annotated, Any, Callable, TypedDict
from pydantic import AfterValidator, BaseModel, Field
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
    if name in functions:
        return functions[name]
    raise ValueError(f"Error: {name} function not found.")


class ReturnsDict(TypedDict):
    type: str


class FunctionsDefinitionDict(TypedDict):
    name: str
    description: str
    parameters: dict[str, dict[str, str]]
    returns: ReturnsDict


class PromptsDict(TypedDict):
    prompt: str


class ParametersValidator(BaseModel):
    name: str = Field(min_length=1)
    type: str = Field(min_length=1)


class FunctionsDefinitionValidator(BaseModel):
    function_name: Annotated[str, AfterValidator(function_validation)] = Field(
        min_length=1
    )
    description: str = Field(min_length=1)
    parameters: list[
        ParametersValidator
    ]  # Potentiellement check si parameters est vraiment obligatoire
    return_type: str = Field(min_length=1)


class PromptValidator(BaseModel):
    content: str = Field(min_length=1)
