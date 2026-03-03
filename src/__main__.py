import sys

from pydantic import ValidationError
from src import parsing


def main(argv: list[str]) -> None:
    try:
        functions_validation = parsing.parse_json_object(
            parsing.file_to_json_object(argv[1])
        )
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
