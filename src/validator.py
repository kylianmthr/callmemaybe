from typing import Annotated, Any, Callable, TypedDict
from pydantic import AfterValidator, BaseModel, Field

functions: dict[str, Callable[..., Any]] = {
    "fn_add_numbers": lambda: print("print"),
    "fn_greet": lambda: print("print2"),
    "fn_reverse_string": lambda: print("print3"),
    "fn_get_square_root": lambda: print("print4"),
    "fn_substitute_string_with_regex": lambda: print("print4"),
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
