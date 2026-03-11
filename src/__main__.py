import re
import sys
from pydantic import ValidationError
from src import parsing
from src.generation import generate_response
from src.llm_sdk import llm_sdk
from src.predict import JSONPredict, Status
from src.stages import (
    DecodeStage,
    EncodingStage,
    LogitsDict,
    LogitsStage,
    NameAndDescriptionStage,
    ParameterStage,
    TokenizationStage,
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
    print("==>", res)
    generated_dictionnary["parameters"] = json.loads(res)
    return generated_dictionnary


def main(argv: list[str]) -> None:
    try:
        llm = llm_sdk.Small_LLM_Model()
        functions = parsing.parse_json_object(
            parsing.file_to_functions_object(argv[1])
        )
        prompts = parsing.parse_prompts(
            parsing.file_to_prompts_object(argv[2])
        )
        # for prompt in prompts:
        #    generated_dictionnary = answer_prompt(
        #        llm, prompt.content, functions
        #    )
        generated_dictionnary = answer_prompt(
            llm, prompts[8].content, functions
        )
        # for func in functions:
        #    allowed_logits += llm.encode(func).tolist()[0]
        # print(allowed_logits)
        print("==== Final res ====")
        print(generated_dictionnary)
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
