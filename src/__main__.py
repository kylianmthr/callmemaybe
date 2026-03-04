import sys
from pydantic import ValidationError
from src import parsing
from src.stages import EncodingStage


def main(argv: list[str]) -> None:
    try:
        functions = parsing.parse_json_object(
            parsing.file_to_functions_object(argv[1])
        )
        prompts = parsing.parse_prompts(
            parsing.file_to_prompts_object(argv[2])
        )
        print(EncodingStage().process(prompts[0].content))
    except (
        FileNotFoundError,
        PermissionError,
        ValueError,
        ValidationError,
        KeyError,
    ) as e:
        print(e)
        exit()


if __name__ == "__main__":
    main(sys.argv)
