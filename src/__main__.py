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


def main(argv: list[str]) -> None:
    try:
        llm = llm_sdk.Small_LLM_Model()
        # functions = parsing.parse_json_object(
        #    parsing.file_to_functions_object(argv[1])
        # )
        functions = {
            "fn_add_numbers": ["a", "b"],
            "fn_greet": ["name"],
            "fn_reverse_string": ["s"],
            "fn_get_square_root": ["a"],
            "fn_substitute_string_with_regex": [
                "source_string",
                "regex",
                "replacement",
            ],
        }
        prompts = parsing.parse_prompts(
            parsing.file_to_prompts_object(argv[2])
        )
        print("=== LLM ===")
        # for func in functions:
        #    allowed_logits += llm.encode(func).tolist()[0]
        # print(allowed_logits)
        initial_prompt = """You must generate a JSON response with this format:
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
        initial_prompt += prompts[2].content
        sentence = initial_prompt
        predict = JSONPredict(
            [
                "name",
                "description",
            ]
        )
        while True:
            if not (len(predict.stack)):
                break
            allowed_logits = []
            logits = LogitsStage().process(
                EncodingStage().process(sentence, llm), llm
            )
            possible_char = predict.get_possible_characters()
            if len(predict.stack):
                if possible_char:
                    for token in possible_char:
                        allowed_logits += llm.encode(token).tolist()[0]
            word = DecodeStage().process(logits, llm, allowed_logits)
            print("==== FREE TEXT ====")
            print(predict.last_key)
            if predict.get_state() == Status.FREE_TEXT and (
                re.search(
                    r'([^" \t]+)"',
                    predict.actual_buffer.split(":")[-1] + word,
                )
            ):
                word = word[: word.find('"') + 1]
            print("\n========== DEBUG ==========")
            # print("=== Logits ===")
            # print("allowed:", allowed_logits)
            print("=== Stack ===")
            print("stack:", predict.stack)
            sentence += word
            print("\n")
            predict.manage_state(word)
        generated_dictionnary = json.loads(
            sentence.replace(initial_prompt, "")
        )
        generated_dictionnary["parameters"] = {}
        predict = JSONPredict(functions[generated_dictionnary["name"]])
        initial_prompt = f'You must generate a JSON response with this format:{{"parameter name": "type of the parameter", ...}} You will use the function {generated_dictionnary["name"]} with this parameters {functions[generated_dictionnary["name"]]}'
        initial_prompt += prompts[2].content
        sentence = initial_prompt
        while True:
            if not (len(predict.stack)):
                break
            allowed_logits = []
            logits = LogitsStage().process(
                EncodingStage().process(sentence, llm), llm
            )
            possible_char = predict.get_possible_characters()
            if len(predict.stack):
                if possible_char:
                    for token in possible_char:
                        allowed_logits += llm.encode(token).tolist()[0]
            word = DecodeStage().process(logits, llm, allowed_logits)
            print("==== FREE TEXT ====")
            print(predict.last_key)
            print("==> predict.keys", predict.keys)
            if predict.get_state() == Status.FREE_TEXT and (
                re.search(
                    r'([^" \t]+)"',
                    predict.actual_buffer.split(":")[-1] + word,
                )
            ):
                word = word[: word.find('"') + 1]
            print("\n========== DEBUG ==========")
            # print("=== Logits ===")
            # print("allowed:", allowed_logits)
            print("=== Stack ===")
            print("stack:", predict.stack)
            sentence += word
            print("\n")
            predict.manage_state(word)
        print(sentence.replace(initial_prompt, ""))
        # predict = JSONPredict()
        # print("stack:", predict.stack)
        # predict.get_input_status("{")
        # print("stack:", predict.stack)
        # predict.get_input_status('"')
        # print("stack:", predict.stack)
        # predict.get_input_status("name")
        # print("stack:", predict.stack)
        # predict.get_input_status('"')
        # print("stack:", predict.stack)
        # predict.get_input_status(':')
        # print("stack:", predict.stack)
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
