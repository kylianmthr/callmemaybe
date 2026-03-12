import sys
from pydantic import ValidationError
from src import parsing
from src.llm_sdk import llm_sdk
from src.stages import (
    NameAndDescriptionStage,
    ParameterStage,
)
import json

from src.validator import FunctionsDefinitionValidator


def answer_prompt(
    model: llm_sdk.Small_LLM_Model,
    prompt: str,
    functions: list[FunctionsDefinitionValidator],
) -> dict:
    generated_dictionnary = {"prompt": prompt}
    res = NameAndDescriptionStage().process(
        prompt,
        model,
        [function.function_name for function in functions],
    )
    generated_dictionnary.update(json.loads(res))
    res = ParameterStage().process(
        prompt,
        model,
        generated_dictionnary["name"],
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
    generated_functions: list[dict],
) -> list[dict]:
    for function in generated_functions:
        stored_func = [
            func
            for func in functions
            if func.function_name == function["name"]
        ][0]
        i = 0
        for parameter in function["parameters"]:
            if stored_func.parameters[i].type == "number":
                function["parameters"][parameter] = int(
                    function["parameters"][parameter]
                )
            i += 1
    return generated_functions


def generate_output_file(filename: str, generated_functions: list[dict]):
    with open(filename, "w") as f:
        json.dump(generated_functions, f, indent=4, ensure_ascii=False)


def main(argv: list[str]) -> None:
    try:
        llm = llm_sdk.Small_LLM_Model()
        functions = parsing.parse_json_object(
            parsing.file_to_functions_object(argv[1])
        )
        prompts = parsing.parse_prompts(
            parsing.file_to_prompts_object(argv[2])
        )
        generated_functions = []
        for prompt in prompts:
            generated_dictionnary = answer_prompt(
                llm, prompt.content, functions
            )
            generated_functions.append(generated_dictionnary)
        # for func in functions:
        #    allowed_logits += llm.encode(func).tolist()[0]
        # print(allowed_logits)
        print(convert_parameters(functions, generated_functions))
        generate_output_file(argv[3], generated_functions)
    except (
        FileNotFoundError,
        ValueError,
        PermissionError,
        ValidationError,
        KeyError,
    ) as e:
        print(type(e), e)
        exit()


if __name__ == "__main__":
    main(sys.argv)
