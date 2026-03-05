import sys
from pydantic import ValidationError
from src import parsing
from src.llm_sdk import llm_sdk
from src.predict import JSONPredict
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
        functions: list[str] = [
            "fn_add_numbers",
            "fn_greet",
            "fn_reverse_string",
            "fn_get_square_root",
            "fn_substitute_string_with_regex",
        ]
        prompts = parsing.parse_prompts(
            parsing.file_to_prompts_object(argv[2])
        )
        print("=== LLM ===")
        # for func in functions:
        #    allowed_logits += llm.encode(func).tolist()[0]
        # print(allowed_logits)
        sentence = """You can choose from these functions:
fn_add_numbers, fn_greet, fn_reverse_string, fn_get_square_root, fn_substitute_string_with_regex.
You must generate a JSON response with this format for each object:
[
  {
    "name": "function name",
    "description": "description of the function",
    "parameters": {
      "something": {
        "type": "number or string"
      }
    },
    "returns": {
      "type": "number or string"
    }
  }
]
"name" (function name),
"description" (description of the function),
"parameters" (the parameters of the function.
It must be objects with this format: \"something\": object, in this object, you have to include \"type\": \"type\". Type can be number or string.)
returns (returns of fthe function.
It must be objects with this format: \"type\": \"type\". Type can be number or string.)
"""
        sentence += prompts[1].content
        predict = JSONPredict()
        last_token = ""
        while True:
            allowed_logits = []
            logits = LogitsStage().process(
                EncodingStage().process(sentence, llm), llm
            )
            predict.get_input_status(last_token)
            if len(predict.stack):
                if predict.stack[-1].value:
                    for token in predict.stack[-1].value:
                        allowed_logits += llm.encode(token).tolist()[0]
            word = DecodeStage().process(logits, llm, allowed_logits)
            print("\n========== DEBUG ==========")
            print("=== Logits ===")
            print("allowed:", allowed_logits)
            print("=== Stack ===")
            print("stack:", predict.stack)
            sentence += word
            last_token = word
            print(sentence)
            print("\n")
            if "}" in word:
                break
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
