import enum
import re

from src.llm_sdk.llm_sdk import Small_LLM_Model


class Status(enum.Enum):
    START = ["{"]
    INSERT_KEY = [
        "name",
        "description",
        "parameters",
        "returns",
        "type",
        "s",
        "a",
        "b",
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
    INSERT_NL = [","]
    INSERT_ONLY_NL = [","]
    END = ["}"]
    FREE_TEXT = None


class JSONPredict:
    def __init__(self) -> None:
        self.stack: list[Status] = [Status.START]
        self.actual_buffer = ""
        self.last_key = ""
        self.model = Small_LLM_Model()
        self.keys = [
            "name",
            "description",
            "parameters",
            "returns",
            "type",
            "s",
            "a",
            "b",
        ]
        self.value = [
            "fn_add_numbers",
            "fn_greet",
            "fn_reverse_string",
            "fn_get_square_root",
            "fn_substitute_string_with_regex",
            "string",
            "number",
            "source_string",
        ]

    def append(self, status: Status) -> None:
        self.stack.append(status)

    def pop(self) -> Status:
        return self.stack.pop()

    def get_state(self) -> Status:
        return self.stack[-1]

    def get_possible_characters(self) -> list[str] | None:
        if self.get_state() == Status.INSERT_KEY:
            return self.keys
        if self.get_state() == Status.INSERT_VALUE:
            return self.value
        else:
            return self.get_state().value

    def manage_state(self, last_token: str) -> bool:
        self.actual_buffer += last_token
        if self.get_state() == Status.START:
            self.pop()
            self.append(Status.INSERT_STRING)
            self.actual_buffer = ""
            return True
        if self.get_state() == Status.INSERT_KEY and re.search(
            r'"\w+$', self.actual_buffer
        ):
            self.pop()
            self.append(Status.INSERT_STRING)
            self.last_key = last_token
            return True
        if self.get_state() == Status.INSERT_STRING and re.search(
            r'"([^"]+)"\s*:\s*"([^"]+)"$', self.actual_buffer
        ):
            self.pop()
            self.append(Status.INSERT_NL)
            return True
        if self.get_state() == Status.INSERT_STRING and re.search(
            r'"\w+"$', self.actual_buffer
        ):
            self.pop()
            self.append(Status.INSERT_SEMI_COLUMN)
            return True
        if self.get_state() == Status.INSERT_SEMI_COLUMN:
            self.pop()
            self.append(Status.INSERT_STRING)
            return True
        if self.get_state() == Status.INSERT_STRING and re.search(
            r'"([^"]+)"\s*:\s*"$', self.actual_buffer
        ):
            self.pop()
            self.keys.remove(self.last_key)
            if self.last_key == "description":
                self.append(Status.FREE_TEXT)
                return True
            self.append(Status.INSERT_VALUE)
            return True
        if (self.get_state() == Status.FREE_TEXT) and re.search(
            r'"([^"]+)"\s*:\s*"([^"]+)"$', self.actual_buffer
        ):
            self.pop()
            self.append(Status.INSERT_NL)
            return True
        if self.get_state() == Status.INSERT_VALUE:
            for possibility in Status.INSERT_VALUE.value:
                if possibility in self.actual_buffer:
                    self.pop()
                    self.append(Status.INSERT_STRING)
        if self.get_state() == Status.INSERT_NL and re.search(
            r'"([^"]+)"\s*:\s*"([^"]+)"\n', self.actual_buffer
        ):
            self.pop()
            self.append(Status.INSERT_STRING)
            self.actual_buffer = ""
            return True
        if self.get_state() == Status.INSERT_NL and re.search(
            r'"([^"]+)"\s*:\s*"([^"]+)",', self.actual_buffer
        ):
            self.pop()
            self.append(Status.INSERT_STRING)
            self.actual_buffer = ""
            return True
        if self.get_state() == Status.INSERT_ONLY_NL:
            self.pop()
            self.append(Status.INSERT_STRING)
            self.actual_buffer = ""
            return True
        if self.get_state() == Status.INSERT_STRING and re.search(
            r'"$', self.actual_buffer
        ):
            # Check si y'a qu'un ". Ca doit etre mis a la fin pour que les autres check soient prio
            self.pop()
            self.append(Status.INSERT_KEY)
            return True
        return False

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
