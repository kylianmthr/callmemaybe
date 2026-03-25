from typing import Any
from pydantic import ValidationError
from src import parsing
from src.llm_sdk import llm_sdk
from src.stages import (
    NameAndDescriptionStage,
    ParameterStage,
)
import json
import sys

from src.validator import FunctionsDefinitionValidator


def answer_prompt(
    model: llm_sdk.Small_LLM_Model,
    prompt: str,
    functions: list[FunctionsDefinitionValidator],
) -> dict[str, str]:
    """
    Process a user prompt and generate a structured response with function
    details.

    This function takes a natural language prompt and identifies the most
    appropriate function to call along with its required parameters.
    It uses a two-stage process:
    first identifying the function name and description,
    then extracting the parameters.

    Args:
        model: A Small_LLM_Model instance used for generating responses.
        prompt: The user's natural language prompt to be processed.
        functions: A list of FunctionsDefinitionValidator objects representing
                  available functions that can be called.

    Returns:
        A dictionary containing:
            - "prompt": The original user prompt
            - "name": The name of the identified function to call
            - "parameters": A dictionary of extracted parameters for
                the function

    Raises:
        IndexError: If no matching function is found in the functions list.
        json.JSONDecodeError: If the LLM responses cannot be parsed as valid
            JSON.
    """
    generated_dictionnary = {"prompt": prompt}
    res = NameAndDescriptionStage().process(prompt, model, functions)
    generated_dictionnary.update(json.loads(res))
    res = ParameterStage().process(
        prompt,
        model,
        generated_dictionnary["name"],
        [
            function.description
            for function in functions
            if function.function_name == generated_dictionnary["name"]
        ][0],
        [
            function.parameters
            for function in functions
            if function.function_name == generated_dictionnary["name"]
        ][0],
    )
    generated_dictionnary["parameters"] = json.loads(res)
    return generated_dictionnary


def convert_parameters(
    functions: list[FunctionsDefinitionValidator],
    generated_functions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Convert parameter types in generated function definitions to match their
    stored function signatures.

    This function iterates through generated function dictionaries and
    converts their parameters
    to the appropriate types (number, boolean) based on the corresponding
    stored function definitions.

    Args:
        functions (list[FunctionsDefinitionValidator]): A list of stored
        function definitions with
            parameter type information.
        generated_functions (list[dict[str, Any]]): A list of generated
        function dictionaries
            containing parameters that need type conversion.

    Returns:
        list[dict[str, Any]]: The modified generated_functions list with
        parameters converted
            to their correct types.

    Behavior:
        - Matches generated functions to stored functions by name
        - Converts "number" type parameters to float
        - Converts "boolean"/"bool" type parameters to Python bool
            (handles "True", "true" strings)
        - Modifies parameters in-place within the function dictionaries
    """
    for function in generated_functions:
        stored_func = [
            func
            for func in functions
            if func.function_name == function["name"]
        ][0]
        i = 0
        for parameter in function["parameters"]:
            if stored_func.parameters[i].type == "number":
                function["parameters"][parameter] = float(
                    function["parameters"][parameter]
                )
            if (
                stored_func.parameters[i].type == "boolean"
                or stored_func.parameters[i].type == "bool"
            ):
                if function["parameters"][parameter] == "True":
                    function["parameters"][parameter] = True
                if function["parameters"][parameter] == "true":
                    function["parameters"][parameter] = True
            i += 1
    return generated_functions


def generate_output_file(
    filename: str, generated_functions: list[dict[str, Any]]
) -> None:
    """
    Writes a list of generated function dictionaries to a JSON file.

    Args:
        filename (str): The path to the output file where the JSON data will
            be written.
        generated_functions (list[dict[str, Any]]): A list of dictionaries,
            each representing a generated function.

    Returns:
        None
    """
    with open(filename, "w") as f:
        json.dump(generated_functions, f, indent=4, ensure_ascii=False)


def main(argv: list[str]) -> None:
    """
    Main entry point for the application. Parses command-line arguments, loads
    function definitions and prompts,
    initializes the language model, processes each prompt to generate function
    call outputs, and writes the results
    to an output file. Handles common file and validation errors gracefully.

    Raises:
        FileNotFoundError: If any of the required files are missing.
        ValueError: If there is an issue with the data format.
        PermissionError: If there are insufficient permissions to access
            files.
        ValidationError: If the input data fails validation.
        KeyError: If expected keys are missing in the data.
    """
    try:
        args = parsing.parse_arguments()
        if not (args.functions_definition):
            args.functions_definition = (
                "src/data/input/functions_definition.json"
            )
        if not (args.input):
            args.input = "src/data/input/function_calling_tests.json"
        if not (args.output):
            args.output = "src/data/output/output.json"
        llm = llm_sdk.Small_LLM_Model()
        try:
            functions = parsing.parse_json_object(
                parsing.file_to_functions_object(args.functions_definition)
            )
            if not len(functions):
                raise ValueError("Functions definition file can't be empty")
            try:
                prompts = parsing.parse_prompts(
                    parsing.file_to_prompts_object(args.input)
                )
                if not len(prompts):
                    raise ValueError("Prompt file can't be empty")
                try:
                    generated_functions = []
                    for prompt in prompts:
                        generated_dictionnary = answer_prompt(
                            llm, prompt.content, functions
                        )
                        generated_functions.append(generated_dictionnary)
                    # for func in functions:
                    #    allowed_logits += llm.encode(func).tolist()[0]
                    # print(allowed_logits)
                    generate_output_file(args.output, generated_functions)
                except Exception as e:
                    print("Error", e)
            except (FileNotFoundError, PermissionError):
                print("Error: Can't open the prompts file.")
            except (json.JSONDecodeError, KeyError):
                print("Error: JSON malformed. (Prompt file)")
            except ValidationError as e:
                print(e.errors()[0]["msg"])
            except Exception as e:
                print("Error:", e)
        except (FileNotFoundError, PermissionError):
            print("Error: Can't open the functions definition file.")
        except (json.JSONDecodeError, KeyError):
            print("Error: JSON malformed. (Functions definition file)")
        except ValidationError as e:
            print(e.errors()[0]["msg"])
        except Exception as e:
            print("Error:", e)
    except (
        FileNotFoundError,
        ValueError,
        PermissionError,
        ValidationError,
    ) as e:
        print(type(e), e)
        exit()
    except Exception as e:
        print("Error while parsing arguments:", e)


if __name__ == "__main__":
    main(sys.argv)
