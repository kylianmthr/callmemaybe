import re
import sys
from pydantic import ValidationError
from src import parsing
from src.llm_sdk import llm_sdk
from src.predict import JSONPredict, Status
from src.stages import (
    DecodeStage,
    EncodingStage,
    LogitsDict,
    LogitsStage,
    TokenizationStage,
)
import json


def generate_response(
    sys_prompt: str, prompt: str, predict: JSONPredict, model: llm_sdk.Small_LLM_Model
) -> str:
    initial_prompt = sys_prompt + prompt
    sentence = initial_prompt
    while True:
        if not (len(predict.stack)):
            break
        allowed_logits = []
        logits = LogitsStage().process(EncodingStage().process(sentence, model), model)
        possible_char = predict.get_possible_characters()
        if len(predict.stack):
            if possible_char:
                for token in possible_char:
                    allowed_logits += model.encode(token).tolist()[0]
        word = DecodeStage().process(logits, model, allowed_logits)
        if predict.get_state() == Status.FREE_TEXT and (
            re.search(
                r'([^" \t]+)"',
                predict.actual_buffer.split(":")[-1] + word,
            )
        ):
            word = word[: word.find('"') + 1]
        sentence += word
        print("==== Actual sentence ====")
        print(sentence)
        print("=========================")
        predict.manage_state(word)
    return sentence.replace(initial_prompt, "")


def main(argv: list[str]) -> None:
    try:
        llm = llm_sdk.Small_LLM_Model()
        # functions = parsing.parse_json_object(
        #    parsing.file_to_functions_object(argv[1])
        # )
        functions = {
            "fn_add_numbers": {
                "parameters": {"a": "number", "b": "number"},
                "returns": "number",
            },
            "fn_greet": {"parameters": {"name": "string"}, "returns": "string"},
            "fn_reverse_string": {"parameters": {"s": "string"}, "returns": "string"},
            "fn_get_square_root": {"parameters": {"a": "number"}, "returns": "number"},
            "fn_substitute_string_with_regex": {
                "parameters": {
                    "source_string": "string",
                    "regex": "string",
                    "replacement": "string",
                },
                "returns": "string",
            },
        }
        prompts = parsing.parse_prompts(parsing.file_to_prompts_object(argv[2]))
        print("=== LLM ===")
        # for func in functions:
        #    allowed_logits += llm.encode(func).tolist()[0]
        # print(allowed_logits)
        sys_prompt = """You must generate a JSON response with this format:
{
    "name": "function name",
    "description": "description of the function"
}
So you have this keys:
"name" (function name, You can choose from these functions:
fn_add_numbers, fn_greet, fn_reverse_string, fn_get_square_root, fn_substitute_string_with_regex),
"description" (description of the function),
You can use the key only one time. You can't repeat the key. DO NOT REPEAT THE KEY. You must use all of the keys
Prefer using , over \n if you want to add another key
"""
        predict = JSONPredict(
            [
                "name",
                "description",
            ],
            [
                "fn_add_numbers",
                "fn_greet",
                "fn_reverse_string",
                "fn_get_square_root",
                "fn_substitute_string_with_regex",
            ],
        )
        res = generate_response(sys_prompt, prompts[8].content, predict, llm)
        generated_dictionnary = json.loads(res)
        predict = JSONPredict(
            list(functions[generated_dictionnary["name"]]["parameters"].keys()),
            list(set(functions[generated_dictionnary["name"]]["parameters"].values())),
        )
        sys_prompt = (
            f"You must generate a JSON response with this format: "
            f'{{"parameter name": "type of the parameter", ...}}. '
            f"Function: {generated_dictionnary['name']}. "
            f"Parameters to type: {functions[generated_dictionnary['name']]['parameters']}. "
            # f"CRITICAL: A Regex is a TEXTUAL pattern. Its data type is ALWAYS a 'string'. "
            f"Use 'number' ONLY for digit-only values (integers/floats)."
        )
        res = generate_response(sys_prompt, prompts[8].content + ".\n", predict, llm)
        generated_dictionnary["parameters"] = json.loads(res)
        predict = JSONPredict(
            ["type"],
            [
                "number",
                "string",
            ],
        )
        sys_prompt = (
            f'You must generate a JSON response with this format: {{"type": "return type"}}. '
            f"The function {generated_dictionnary['name']} {generated_dictionnary['description']}"
            f"Therefore, the return type is '{functions[generated_dictionnary['name']]['returns']}'. "
            f"Choose between 'number' or 'string'."
        )
        res = generate_response(sys_prompt, prompts[8].content + ".\n", predict, llm)
        generated_dictionnary["returns"] = json.loads(res)
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
