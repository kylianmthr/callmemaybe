import enum
import re

from src.llm_sdk.llm_sdk import Small_LLM_Model


class Status(enum.Enum):
    START = ["{"]
    OBJECT = [
        " ",
        '"',
        "name",
        "description",
        "parameters",
        "returns",
        "type",
        ",",
        "\n",
        "\t",
        "}",
        "s",
        "a",
        "b",
        ":",
    ]
    INSERT_STRING = ['"']
    INSERT_SEMI_COLUMN = [":"]
    INSERT_VALUE = [
        "fn_add_numbers",
        "fn_greet",
        "fn_reverse_string",
        "fn_get_square_root",
        "fn_substitute_string_with_regex",
        "string",
        "number",
        "source_string",
    ]
    FREE_TEXT = None


class JSONPredict:
    def __init__(self) -> None:
        self.stack: list[Status] = []
        self.stack.append(Status.START)
        self.actual_line = ""
        self.model = Small_LLM_Model()

    def append(self, status: Status) -> None:
        self.stack.append(status)

    def pop(self) -> Status:
        return self.stack.pop()

    def get_input_status(self, last_token: str, i: int = 0) -> bool:
        if re.search("{", last_token):
            print("1")
            self.stack.pop()
            self.stack.append(Status.INSERT_STRING)
            return True
        elif re.search('"(.*?)"', last_token) and ":" not in last_token:
            print("2")
            self.stack.append(Status.INSERT_SEMI_COLUMN)
            return True
        elif re.search("}", last_token):
            print("3")
            self.stack.pop()
            return True
        elif (
            re.search('"([^"]+)"\s*:', last_token)
            and last_token[-1] == Status.INSERT_SEMI_COLUMN
        ):
            print("4")
            self.stack.pop()
            return True
        elif re.search('"(description+)"\s*:$', last_token):
            print("5")
            self.stack.append(Status.FREE_TEXT)
            return True
        elif re.search('"([^"]+)"\s*:$', last_token):
            print("6")
            print("->", last_token)
            self.stack.append(Status.INSERT_VALUE)
            return True
        elif re.search('"([^"]+)"\s*:\s*"([^"]+)"', last_token):
            print("7")
            self.stack.pop()
            return True
        elif i == 1:
            return False
        elif last_token == '"' and self.stack[-1] == Status.INSERT_STRING:
            print("8")
            self.stack.pop()
            self.stack.append(Status.OBJECT)
            self.actual_line += last_token
            return True
        elif re.search('"([^"]+)$', last_token):
            self.stack.pop()
            return True
        elif re.search('"\w+', last_token):
            self.stack.append(Status.OBJECT)
            self.actual_line += last_token
            return True
        else:
            self.actual_line += last_token
            line_status = self.get_input_status(self.actual_line, 1)
            print("Line:", self.actual_line)
            if line_status:
                if (
                    self.stack[-1] != Status.INSERT_SEMI_COLUMN
                    and self.stack[-1] != Status.INSERT_VALUE
                    and self.stack[-1] != Status.FREE_TEXT
                ):
                    self.actual_line = ""
                return True
        return False
