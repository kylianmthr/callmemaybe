import sys
from pydantic import ValidationError
from src import parsing
from src.llm_sdk import llm_sdk
from src.stages import (
    EncodingStage,
    LogitsDict,
    LogitsStage,
    LogitsToWordStage,
)
import json


def main(argv: list[str]) -> None:
    try:
        llm = llm_sdk.Small_LLM_Model()
        functions = parsing.parse_json_object(
            parsing.file_to_functions_object(argv[1])
        )
        prompts = parsing.parse_prompts(
            parsing.file_to_prompts_object(argv[2])
        )
        print("=== LLM ===")
        print("- Prompt:", prompts[1])
        sentence = "You must resume your responses."
        sentence += prompts[1].content
        while True:
            logits = LogitsStage().process(
                EncodingStage().process(sentence, llm), llm
            )
            max_logits = max(logits)
            if max_logits == 151645:
                break
            word = LogitsToWordStage().process(logits, llm)
            sentence += word
            print(sentence)
    except (
        FileNotFoundError,
        PermissionError,
        ValueError,
        ValidationError,
        KeyError,
    ) as e:
        print(type(e), e)
        exit()


if __name__ == "__main__":
    main(sys.argv)
